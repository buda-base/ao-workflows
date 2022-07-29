"""Operations for the iiifpres crawl"""
import logging
from datetime import time

from dagster import op, job, get_dagster_logger, List, Dict, String, Any, repository, asset, define_asset_job

from crawl_utils import crawl_utils

s3_session: crawl_utils = crawl_utils()

from dagster import asset

@asset(
    metadata={"owner":"jmk@tbrc.org","domain": "ao"}
)
def works():
    work_list:[] = []
    with open('data/scans.lst', 'r') as df:
        work_list = [x.strip() for x in df.readlines()]
    get_dagster_logger().info(f"retrieved {len(work_list)} works")
    return work_list

@asset(
    metadata={"owner":"jmk@tbrc.org","domain": "ao", "help" : "Contains the status of all the dimensions.json scanned"}
)
def scan_results(works):
    get_dagster_logger().info(f"scanning {len(works)} works")
    start = time.time()
    scanned_works =  test_works(works)
    end = time.time()
    get_dagster_logger().info("done scanning %d works. Took %12.3 sec" % (len(works), float(end - start)))

    # Because I'm nervous,
    get_dagster_logger().info(scanned_works)
    start = time.time()
    if get_dagster_logger().isEnabledFor(logging.DEBUG):
        with open('scanlog.json', 'w') as nerv:
            import json
            blarg = json.dumps(scanned_works)
            get_dagster_logger().info(blarg)
            get_dagster_logger().info("writing log file")
            nerv.write(blarg)

    end = time.time()
    get_dagster_logger().info("done writing assets file of %d results. Took %12.3 sec" % (len(works), float(end - start)))


    return scanned_works

# TODO: Defines ins and outs for ops
@op
def get_works() -> List[String]:
    """
    One operation to get all the works. Just uses the asset
    :return: works
    """

    work_list: [] = []
    with open('data/scans.lst', 'r') as df:
        work_list = [x.strip() for x in df.readlines()]

    return work_list[0:2]


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

    # Test 1: Are all the file names in order?
    filenames: [] = [x["filename"] for x in dims]
    sort_test_pass = all(filenames[i] < filenames[i+1] for i in range(len(filenames) - 1))

    # Test 2: does each filename have a valid height and width?
    has_image_dims: bool = all([validate_dim_int(x, "height") and validate_dim_int(x, "width") for x in dims])

    return sort_test_pass and has_image_dims, f"sorted:{sort_test_pass} has_dims:{has_image_dims}"


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
    # get_dagster_logger().info(f"valid:{valid}, path:{dim_s3_path} reasons:{reasons}")
    return valid


@op
def test_works(ws: List[String]) -> List[Dict]:
    out: [] = []
    for w in ws:
        aresult: {} = test_work_json(w)
        # get_dagster_logger().info(aresult)
        out.append(aresult)
    return out


@job
def iiifpres_crawl():
    w = get_works()
    test_works(w)

scan_works_job= define_asset_job(name="scan_works", selection="scan_results")

@repository
def iiif_crawl_repo():
    return [works, scan_results, scan_works_job, iiifpres_crawl]


if __name__ == '__main__':
    result = iiifpres_crawl.execute_in_process()
