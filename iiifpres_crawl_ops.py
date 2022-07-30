"""Operations for the iiifpres crawl"""
import sys
from datetime import *

from dagster import op, job, get_dagster_logger, List, Dict, String, repository, define_asset_job, AssetIn

from crawl_utils import crawl_utils

s3_session: crawl_utils = crawl_utils()

from dagster import asset


@asset(
    metadata={"owner": "jmk@tbrc.org", "domain": "ao"}
)
def works():
    work_list: [] = []
    with open('data/scans.lst', 'r') as df:
        work_list = [x.strip() for x in df.readlines()]
    get_dagster_logger().info(f"retrieved {len(work_list)} works")
    return work_list


@asset(
    ins={"works_to_scan": AssetIn("works")},
    metadata={"owner": "jmk@tbrc.org", "domain": "ao", "help": "Creates validation result asset"}
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


@job
def iiifpres_crawl():
    scan_works(works())


scan_works_job = define_asset_job(name="scan_works_job", selection="scan_works")


@repository
def iiif_crawl_repo():
    return [works, scan_works, scan_works_job, iiifpres_crawl]

