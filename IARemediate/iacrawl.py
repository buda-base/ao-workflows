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

from dagster import define_asset_job, job, asset, repository

from iaCrawlUtils import ia_report_log, ia_lib


@asset
def mismatch_data():
    log = ia_report_log(Path(Path.home() / "dev" / "ao-workflows" / "data" / "ia-mismatch.report.log"))
    results = log.raw_lines
    return results


@asset
def mismatches(mismatch_data):
    results: {} = {}
    cur_reason: str = 'base reason:'
    results[cur_reason] = set()
    for _line in mismatch_data:
        if _line.startswith('bdrc'):
            results[cur_reason].add(_line)
        else:
            # add a new reason
            cur_reason = _line
            results[cur_reason] = set()
    return results


@asset
def item_mismatches(mismatches):
    results: {} = {}

    # items() is an iterator of unnamed tuples
    for item in mismatches.items():
        k = item[0]
        for w in item[1]:
            if w not in results.keys():
                results[w] = set()
            results[w].add(k)
    return results


@asset
def items_with_failed_derive(item_mismatches):
    """
    Get the last derive step for each item. If it failed its last derive,
    Add it to the list
    :param item_mismatches: mismatched inversion, keyed by item number
    :return:
    """
    ia_sess: ia_lib = ia_lib()
    y = []
    iTries = 0
    for x in item_mismatches.items():
        if ia_sess.get_last_work_derive_task(x[0]).color is not None:
            y.append(x)
        iTries += 1
        if iTries == 10:
            break
    return y


mismatch_job = define_asset_job(name="get_raw_mismatches_job", selection="mismatch_data")
items_for_mismatch = define_asset_job(name="mismatched_items", selection="mismatches")
mismatch_for_items = define_asset_job(name="mismatches_for_items", selection="item_mismatches")


@job
def some_ia_action():
    """
    Stub - not called directly
    :return:
    """
    x = items_with_failed_derive(item_mismatches(mismatches(mismatch_data())))


@repository
def ia_fix_repo():
    return [some_ia_action, mismatch_job, items_for_mismatch, mismatch_for_items,
            mismatch_data, mismatches, item_mismatches]


if __name__ == '__main__':
    some_ia_action.execute_in_process()
