"""Operations for the iiifpres crawl"""
import sys
from datetime import *

from dagster import job, get_dagster_logger, List, Dict, repository, define_asset_job, AssetIn

from crawl_utils import crawl_utils

s3_session: crawl_utils = crawl_utils()

from dagster import asset


@asset(
    metadata={"owner": "jimk@tbrc.org", "domain": "ao"},
    group_name='iiif_pres'
)
def works():
    work_list: [] = []
    with open('data/scans.lst.full', 'r') as df:
        work_list = [x.strip() for x in df.readlines()]
    get_dagster_logger().info(f"retrieved {len(work_list)} works")
    return work_list


@asset(
    ins={"works_to_scan": AssetIn("works")},
    metadata={"owner": "jimk@tbrc.org", "domain": "ao", "help": "Creates validation result asset"},
    group_name='iiif_pres'
)
def scan_works(works_to_scan) -> List[Dict]:
    """
    Main test loop
    :param ws:
    :return:
    """
    out: [] = []
    in_error: bool = False

    time_stamp = date.strftime(datetime.now(), "%y-%m-%d_%H-%M-%S")
    try:
        for w in works_to_scan:
            aresult: {} = test_work_json(w)
            # Test error handling
            # if len(out) > 50:
            #     raise ValueError("testing write on fail")
            out.append(aresult)
    except:
        ei = sys.exc_info()
        in_error = True
        get_dagster_logger().error(f"test_all_works: Unhandled Exception class: {ei[0]}, message: {ei[1]} ")
    finally:
        try:

            # Export whatever we got so far, even if in error
            with open(f"{time_stamp}.dat", "w") as out_dat:
                out_dat.writelines([str(x) + '\n' for x in out])
        except:
            ei = sys.exc_info()
            get_dagster_logger().error(f"test_all_works_dump: Unhandled Exception class: {ei[0]}, message: {ei[1]} ")
        finally:
            get_dagster_logger().info(f"scan_works step:  success: {not in_error}")

        # Save what we have
    return out


def get_image_groups(work: str) -> []:
    """
    Return the s3 paths to the image groups in the work
    :param work:
    :return: keys for each image group's dimensions.json
    """
    return s3_session.get_dimensions_s3_keys(work)


def test_work_json(work: str) -> {}:
    """
    Test all the work's jsons
    :param work:
    :return:
    """
    ig_results: [] = [{"image_group": x, "valid": test_ig_dim(x)} for x in get_image_groups(work)]
    return {"work": work, "valid": all([x["valid"] for x in ig_results]), "ig_results": ig_results}


def validate_dims(dims: []) -> ():
    """
    Run validation tests against a complete dimensions
    :param dims:
    :return:
    """

    sort_test_pass: bool
    has_image_dims: bool

    try:
        # Test 1: Are all the file names in order?
        filenames: [] = [x["filename"] for x in dims]
        sort_test_pass = all(filenames[i] < filenames[i + 1] for i in range(len(filenames) - 1))

        # Test 2: does each filename have a valid height and width?
        has_image_dims: bool = all([validate_dim_int(x, "height") and validate_dim_int(x, "width") for x in dims])
        return sort_test_pass and has_image_dims, f"sorted:{sort_test_pass} has_dims:{has_image_dims}"
    except KeyError:
        # Probably failed to get anything at all
        return False, f"{dims}"


def validate_dim_int(dict_entry: {}, attr: str) -> bool:
    """
    Validates one dimensions dictionary entry for state of positive integer
    :param dict_entry: volume-manifest-entry for one file
    :return: true if the node is complete
    """
    try:
        return int(dict_entry[attr]) > 0
    except ValueError:
        pass
    except KeyError:
        pass
    return False


def test_ig_dim(dim_s3_path: str) -> bool:
    """

    :param dim_s3_path:
    :return:
    """
    dim_values: [] = s3_session.get_dimension_values(dim_s3_path)
    #
    # IMPORTANT: These are the set of validations we perform:
    valid, reasons = validate_dims(dim_values)
    get_dagster_logger().info(f"valid:{valid}, path:{dim_s3_path} reasons:{reasons}")
    return valid


@asset(
    group_name='iiif_pres')
def failed_works(scan_works):
    """
    Summarizes the scan_works_job asset job results
    :return:
    """
    failed_works = [i for i in scan_works if not dict(i)['valid']]
    get_dagster_logger().info(f"Number of failed works {len(failed_works)}")
    return failed_works


@asset(group_name='iiif_pres')
def failed_image_groups(failed_works):
    """
    Extracts each failed image group
    :param failed_works: scan structures whose 'valid' is False
    :return []:
    """
    # results = [i for i in [x['ig_results'] for x in failed_works ] if not i['valid']]
    # for x in bb:
    #     [cc.append(i) for i in x]
    results: [] = []
    for f in failed_works:
        get_dagster_logger().info(f"One works worth of ig results {f['ig_results']}")
        for ig_result in f['ig_results']:
            if not ig_result['valid']:
                get_dagster_logger().info(f"one ig result {ig_result}")
                results.append(ig_result['image_group'])
            # for r in ig_result:
            #     get_dagster_logger().info( f"One result{r}")

            # if  not r['valid']:
            #     results.append(r['image_group'])

            #        [results.append(i) for i in [ g['igresults'] for g in f  ]
    get_dagster_logger().info(f"Number of failed image groups {len(results)}")

    return results


def parse_ig(ig_path: str) -> str:
    """
    Parse an image group path to get its image group. The image group is the parent of the dimensions.json
    :param ig_path:
    :return:
    """
    from pathlib import Path

    return Path(ig_path).parent.name


@asset(ins={"failed_works": AssetIn(key="failed_works")},
    group_name='iiif_pres')
def failed_work_ids(failed_works):
    """
    Extract [ { 'work': work , 'image_groups' :[ ig1 } ...] from failed_work data
    :param failed_works:
    :return:
    """
    results: [] = []
    for f in failed_works:
        # get_dagster_logger().info(f)
        results.append(
            {'work': f['work'], 'igs': [parse_ig(x['image_group']) for x in f['ig_results'] if not x['valid']]})
        # for ig_result in f['ig_results']:
        #     if not ig_result['valid']:
        #         igs:[] = map(parse_ig,ig_result['image_group'])
        #
        #         get_dagster_logger().info(f"one ig result {ig_result}")
        #         igs.append(ig_result['image_group'])
    [get_dagster_logger().info(x) for x in results]
    return results


@asset(
    group_name='iiif_pres')
def fixed_image_groups(failed_image_groups):
    """
    Fixes the failed image groups
    :param failed_image_groups: [ { 'ig_name': 'path' : s3_path } ]
    :return:
    """
    for fig in failed_image_groups:
        get_dagster_logger().info(fig)


# ({"work_igs": AssetIn(key="failed_work_ids")}))
# What do I get if I just pass the materialized asset as an unnamed parm?
# (ins={'work_igs': In(asset_key=AssetKey(['failed_work_ids']))})

@asset(
    group_name='iiif_pres')
def fix_igs(failed_work_ids):
    """
    Actually fix the bad image groups
    :param failed_work_ids [ { 'work' : work , 'igs' : [ image_group..]} ]
    :return:
    """
    for work_ig in failed_work_ids:
        for ig in work_ig['igs']:
            get_dagster_logger().info(f"Fixing {ig}")
            s3_session.fix_one(work_ig['work'], ig)



@job
def iiifpres_crawl():
    """
    Materialize scan works. Not used directly. Run scan_works_job from UI instead
    :return:
    """
    # fixed_image_groups(failed_image_groups(failed_works(scan_works(works()))))
    fix_igs(failed_work_ids(failed_works(scan_works(works()))))


scan_works_job = define_asset_job(name="scan_works_job", selection="scan_works")
fixed_works_job = define_asset_job(name="fixed_works_job", selection="fixed_works")
fixed_igs_job = define_asset_job(name="fixed_igs_job", selection="fixed_igs")


@repository
def iiif_crawl_repo():
    return [works, scan_works, scan_works_job, iiifpres_crawl, failed_works, failed_image_groups, failed_work_ids,
            fix_igs]


#
# TODO:
# How to materialize works in the API

if __name__ == '__main__':
    iiifpres_crawl.execute_in_process()
