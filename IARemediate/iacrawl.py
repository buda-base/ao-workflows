"""
Workflow for https://github.com/buda-base/ao-workflows/issues/2
1. Build the input dictionary
2. Get the derive status for all them
3. Sort into succeeded and failed derives
4. Build an export list (csv) of the failed derives
5. For the succeeded derives
    a. Issue the ia tasks derive task args


"""
import os
from pathlib import Path

from dagster import job, asset, repository, get_dagster_logger, op, materialize

from IaTrack import IATracker
from iaCrawlUtils  import IaReportLog, ia_lib


@asset(group_name='ia_crawl')
def mismatch_data():
    log = IaReportLog(Path(Path.home() / "dev" / "ao-workflows" / "data" / "ia-mismatch.report.txt"))
    # log = IaReportLog(Path(Path.home() / "dev-from-deploy" / "ao-workflows" / "data" / "ia-mismatch.report.txt"))
    results = log.raw_lines
    get_dagster_logger().info(f"loaded {len(results)} lines from log")
    return results


@asset(group_name='ia_crawl')
def mismatches(mismatch_data):
    """
    Turns raw mismatch data into data structure
    :type mismatch_data: [str]
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
    results = list(mismatched_as_set - failed_derive_set)
    get_dagster_logger().info(f"found {len(results)} mismatches where derive was successful.")
    return results

    # , input_manager_key="io_manager")},
    # required_resource_keys={"io_manager"}


# (ins={"mismatch_needs_rederive": In(asset_key=AssetKey(["mismatched_items_that_derived"]))})
@op
def do_launch(mismatch_needs_rederive):
    """
    Launch rederive for mismatches. Hank advises 200 rederives ok.
    :return:
    """

    ia_ctx = ia_lib()
    ia_db: IATracker = IATracker()

    successes: int = 0
    for mmnd in mismatch_needs_rederive:
        try:
            task_id, task_log = ia_ctx.submit_rederive_task(mmnd)
            ia_db.add_track(mmnd, mmnd.strip("bdrc-"), int(task_id), task_log)
            successes += 1
        except Exception as eek:
            get_dagster_logger().error(f"Rederive request for {mmnd} error:{eek} ")

    get_dagster_logger().info(f"rederive requests:  succeeded:{successes}  failed:{len(mmnd) - successes}")


@job
def launch_rederives():
    do_launch()


@repository
def ia_fix_repo():
    # return [some_ia_action, mismatch_job, items_for_mismatch, mismatch_for_items,
    #         mismatch_data, mismatches, item_mismatches]
    #
    # defining one job for all assets
    return [
        mismatch_data,
        mismatches,
        item_mismatches,
        items_with_failed_derive,
        mismatched_items_that_derived,
        launch_rederives

    ]


if __name__ == '__main__':
    # ------------------ Run job on materialized assets

    # get_dagster_logger().info(f"Here comes the job")
    # launch_rederives.execute_in_process(run_config={
    #     'ops': {
    #         'do_launch':
    #             {
    #                 'inputs': {'mismatch_needs_rederive': {'pickle': {
    #                     'path': str(Path(os.getenv('DAGSTER_HOME')) / 'storage' / 'mismatched_items_that_derived')}}
    #                 }
    #             }
    #     }
    # }
    # )
    # -------------------- Asset materialization for debug session
    get_dagster_logger().info(f"materializing")
    # mismatch_for_items.ex
    assets = [
        mismatch_data,
        mismatches,
        item_mismatches,
        items_with_failed_derive,
        mismatched_items_that_derived,
    ]

    # Rebuild from scratch
    result = materialize(assets)
    # Try - nope: says upstream not materialized
    # results = materialize([mismatched_items_that_derived])
