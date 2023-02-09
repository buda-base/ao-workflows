"""
Helper utilities for workflow
"""
import os
import pickle
from pathlib import Path

import requests
import logging
from BdrcDbLib.DbOrm.models.DrsProjectMgmt import Projects, ProjectMembers, ProjectTypes, MemberTypes
from BdrcDbLib.DbOrm.DrsContextBase import DrsDbContextBase

from requests import Response

# %(pathname)s Full pathname of the source file where the logging call was issued(if available).
#
# %(filename)s Filename portion of pathname.
#
# %(module)s Module (name portion of filename).
#
# %(funcName)s Name of function containing the logging call.
#
# %(lineno)d Source line number where the logging call was issued (if available).

logging.basicConfig(datefmt='%Z: %Y-%m-%d %X', format='[%(asctime)s]{%(module)s.%(funcName)s:%(lineno)d}%(levelname)s:%(message)s',
                    level=logging.INFO)

def costly_resources(*args) -> []:
    """
    Cache for costly resources
    :return: [GB eligible work Names] if not *args,
    [DbOrm.models.drs.Works Matching *args] (sqlAlchemy.works)]
    """
    import shelve

    costlies = shelve.open(os.path.expanduser("~/tmp/costlies"),writeback=True)  # open -- file may get suffix added by low-level
    # library

    gb_c_key = "GB_Candidates"
    w_key = "GB_Works"

    # Load the cache

    # If we dont have the candidates, put them into the sheld
    if not gb_c_key in costlies.keys():
        try:
            gb_ready: Response = requests.get(BUDA_Get_GB_ReadyUrl)
            costlies[gb_c_key] = gb_ready.text.split('\n')
        except requests.HTTPError as e:
            if e.response.status_code != 404:
                raise
            costlies[gb_c_key] = []
        costlies.sync()

    # If we don't have the resulting works
    if args:
        if not w_key in costlies.keys():
            # load the cache
            with DrsDbContextBase() as ctx:

                # args is a tuple - the first element is the list
                costlies[w_key] = [x.workId for x in [ctx.get_or_create_work(y) for y in args[0]]]
            costlies.sync()
    # Pick the return
    dict_entry = w_key if args else gb_c_key
    return costlies[dict_entry]




def dequote(s: str) -> str:
    """
    If a string has single or double quotes around it, remove them.
    Make sure the pair of quotes match.
    If a matching pair of quotes is not found,
    or there are less than 2 characters, return the string unchanged.
    [thanks to stackoverflow](https://stackoverflow.com/questions/3085382/how-can-i-strip-first-and-last-double-quotes)
    """
    if (len(s) >= 2 and s[0] == s[-1]) and s.startswith(("'", '"')):
        return s[1:-1]
    return s


# Can import as csv_f, json, or simple csv (one column)
BUDA_Get_GB_ReadyUrl: str = "https://purl.bdrc.io/query/table/AO_okforGB?&format=csv&pageSize=20000"
buda_work_prefix: str = "bdr:"


def gb_proj_candidates() -> []:
    """
    Extract from BUDA
    :return:
    """
    return costly_resources()


def gb_transform(in_list: [str]) -> int:
    """
    Transforms works into workIds
    :param in_list: "some lines"+"bdr:Wnnnn"+
    :type in_list:[str]
    :return: for every element containing bdr: return the work Id that goes with that work.
    Creates the work if needed
    """
    # nasty, filthy, dirty input
    in_list = [dequote(x) for x in in_list]

    # 1. Remove everything that's not a work, and remove the prefix
    work_elems = [x[len(buda_work_prefix):] for x in in_list if x.startswith(buda_work_prefix)]
    return costly_resources(work_elems)


def gb_load(work_ids: [str], project_name: str):
    """
    Defines the GB Metadata project
    :param workIds: work keys
    :param project_name:
    :return:
    """
    from sqlalchemy import select
    from sqlalchemy_get_or_create import get_or_create
    proj_sel = select(Projects).where(Projects.name == project_name)
    with DrsDbContextBase() as ctx:
        ptype = select(ProjectTypes).where(ProjectTypes.project_type_name == "Distribution")
        pmtype = select(MemberTypes).where(MemberTypes.m_type == "Work")

        project_type = ctx.session.scalars(ptype).first()
        project_member_type = ctx.session.scalars(pmtype).first()

        defaults = {
            'project_type': project_type,
            'm_type': project_member_type
        }
        o, newly_made = get_or_create(ctx.session, Projects, defaults=defaults, name=project_name)
        if newly_made:
            rstr = "Created"
        else:
            rstr = "Found"
        logging.info(f"{rstr} project {o}")

        for work_id in work_ids:
            ctx.session.add(ProjectMembers(pm_work_id=work_id, project=o))
        ctx.session.commit()


# Just invoke for testing
if __name__ == '__main__':
    werke = gb_transform(gb_proj_candidates())
    gb_load([werke[0]], "Google Books Metadata")
