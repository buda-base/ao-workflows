"""
Workflow for https://github.com/buda-base/ao-workflows/issues/2
1. Build the input dictionary
2. Get the derive status for all them
3. Sort into succeeded and failed derives
4. Build an export list (csv) of the failed derives
5. For the succeeded derives
    a. Issue the ia tasks derive task args


"""
from pathlib import Path

from dagster import define_asset_job, job, asset, repository, materialize, get_dagster_logger

from iaCrawlUtils import ia_report_log, ia_lib


@asset(group_name='ia_crawl')
def mismatch_data():
    log = ia_report_log(Path(Path.home() / "dev" / "ao-workflows" / "data" / "ia-mismatch.report.txt"))
    # log = ia_report_log(Path(Path.home() / "dev-from-deploy" / "ao-workflows" / "data" / "ia-mismatch.report.txt"))
    results = log.raw_lines
    get_dagster_logger().info(f"loaded {len(results)} lines from log")
    return results


@asset(group_name='ia_crawl')
def mismatches(mismatch_data):
    """
    Turns raw mismatch data into data structure
    :param mismatch_data: [textline, ..... ]
    :return: { reason: [item_id, ....] }
    """
    results: {} = {}
    cur_reason: str = 'base reason:'
    results[cur_reason] = set()
    total_mismatches: int = 0
    for _line in mismatch_data:
        if _line.startswith('bdrc'):
            results[cur_reason].add(_line)
            total_mismatches += 1
        else:
            # add a new reason
            cur_reason = _line
            results[cur_reason] = set()

    get_dagster_logger().info(f"Calculated {len(results)} reasons, {total_mismatches} works")
    return results


@asset(group_name='ia_crawl')
def item_mismatches(mismatches):
    """
    Iterates mismatches
    :param mismatches: {reason : [item id, ....], .... }
    :return: { item_id: [reason, ..... ] }
    """
    results: {} = {}

    total_work_mismatches: int = 0
    # items() is an iterator of unnamed tuples
    for item in mismatches.items():
        k = item[0]
        for w in item[1]:
            if w not in results.keys():
                results[w] = set()
            results[w].add(k)
            total_work_mismatches += 1
    get_dagster_logger().info(f"found {len(results)} mismatched items, with a total of {total_work_mismatches} reasons")
    return results


@asset(group_name='ia_crawl')
def items_with_failed_derive(item_mismatches):
    """
    Get the last derive step for each item. If it failed its last derive,
    Add it to the list
    :param item_mismatches:  { item_id: [reason, ..... ] }
    :return: [item IA id,...]
    """
    ia_sess: ia_lib = ia_lib()
    y = []
    for x in item_mismatches.items():
        if ia_sess.get_last_work_derive_task(x[0]).color is not None:
            y.append(x[0])
        # if len(y) > 10:
        #     break

    get_dagster_logger().info(f"found {len(y)} items that failed derive.")
    return y

@asset(group_name='ia_crawl')
def mismatched_items_that_derived(item_mismatches, items_with_failed_derive):
    """
    returns the items which were mismatched and also did derive
    :param item_mismatches: [{ item_id: [reasons,...]}
    :param items_with_failed_derive: [item_id,...]
    """
    mismatched_as_set = set(item_mismatches.keys())
    failed_derive_set = set(items_with_failed_derive)
    results  = list (mismatched_as_set - failed_derive_set)
    get_dagster_logger().info(f"found {len(results)} mismatches where derive was successful.")
    return results


#
# mismatch_job = define_asset_job(name="get_raw_mismatches_job", selection="mismatch_data")
# items_for_mismatch = define_asset_job(name="mismatched_items", selection="mismatches")
# mismatch_for_items = define_asset_job(name="mismatches_for_items", selection="item_mismatches")

#
# @job
# def some_ia_action():
#     """
#     Stub - not called directly
#     :return:
#     """
#     x = items_with_failed_derive(item_mismatches(mismatches(mismatch_data())))
#


@repository
def ia_fix_repo():
    # return [some_ia_action, mismatch_job, items_for_mismatch, mismatch_for_items,
    #         mismatch_data, mismatches, item_mismatches]
    #
    # defining one job for all assets
    return [mismatch_data, mismatches, item_mismatches, items_with_failed_derive, mismatched_items_that_derived]


if __name__ == '__main__':
    # mismatch_for_items.ex
    assets = [
        mismatch_data,
        mismatches,
        item_mismatches,
        items_with_failed_derive,
        mismatched_items_that_derived,
    ]

    get_dagster_logger().info(f"materializing")

    # Rebuild from scratch
    result = materialize(assets)
    # Try - nope: says upstream not materialized
    # results = materialize([mismatched_items_that_derived])
