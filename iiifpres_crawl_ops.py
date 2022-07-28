"""Operations for the iiifpres crawl"""

from dagster import op, job, get_dagster_logger, List, Dict
from bdrc_works import works
from crawl_utils import crawl_utils

s3_session: crawl_utils = crawl_utils()


# TODO: Defines ins and outs for ops
@op
def get_works() -> List:
    """
    One operation to get all the works. Just uses the asset
    :return: works asset
    """
    return works()


@op
def get_image_groups(work: str) -> List:
    """
    Return the s3 paths to the image groups in the work
    :param work:
    :return: keys for each image group's dimensions.json
    """
    s3_session.get_dimensions_s3_keys(work)


@op
def test_work_json(work: str) -> Dict:
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
    filenames:[] = [ x["filename"] for x in dims]
    sort_test_pass = sorted(filenames)

    # Test 2: does each filename have a valid height and width?
    has_image_dims: bool = all([validate_dim_int(x, "height") and validate_dim_int(x, "width") for x in dims])

    return sort_test_pass and has_image_dims , f"sorted:{sort_test_pass} has_dims:{has_image_dims}"


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


@op
def test_ig_dim(dim_s3_path: str) -> bool:
    """

    :param dim_s3_path:
    :return:
    """
    dim_values:[] = crawl_utils.get_dimension_values(dim_s3_path)
    #
    # IMPORTANT: These are the set of validations we perform:
    valid, reasons =  validate_dims(dim_values)
    get_dagster_logger().info(f"valid:{valid}, path:{dim_s3_path} reasons:{reasons}")
    return valid




@job
def iiifpres_crawl():
    get_works().map(test_work_json)


if __name__ == '__main__':
    result = iiifpres_crawl.execute_in_process()
