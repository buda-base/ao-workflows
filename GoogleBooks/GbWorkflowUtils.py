"""
Helper utilities for workflow
"""
import os
import pickle
from pathlib import Path

import BdrcDbLib.DbOrm.models.drs
import requests
import logging
from BdrcDbLib.DbOrm.models.DrsProjectMgmt import Projects, ProjectMembers, ProjectTypes, MemberTypes, MemberStates
from BdrcDbLib.DbOrm.DrsContextBase import DrsDbContextBase, Volumes

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
from sqlalchemy.future import select

logging.basicConfig(datefmt='%Z: %Y-%m-%d %X',
                    format='[%(asctime)s]{%(module)s.%(funcName)s:%(lineno)d}%(levelname)s:%(message)s',
                    level=logging.DEBUG)

COSTLY_CANDIDATES = "GB_Candidates"
COSTLY_WORKS = "GB_Works"
COSTLY_VOLUMES = "GB_Volumes"

# Work features
from collections import namedtuple
WorkBit = namedtuple('WorkBit', 'id name')

def get_volumes_for_work(work_bit: WorkBit) -> [Volumes]:
    """
    Given a work id and name, get the volumes that go with it.
    :param work_bit:
    :return: Volume DAOs
    """

def costly_resources(key: str, *args) -> []:
    """
    Cache for costly resources
    :return: [GB eligible work Names] if not *args,
    [DbOrm.models.drs.Works Matching *args] (sqlAlchemy.works)]
    """
    import shelve

    costlies = shelve.open(os.path.expanduser("~/tmp/costlies"),
                           writeback=True)  # open -- file may get suffix added by low-level

    # Load the cache

    # If we dont have the candidates, put them into the shelf
    if key == COSTLY_CANDIDATES:
        if not COSTLY_CANDIDATES in costlies.keys():
            try:
                gb_ready: Response = requests.get(BUDA_Get_GB_ReadyUrl)
                costlies[COSTLY_CANDIDATES] = gb_ready.text.split('\n')
            except requests.HTTPError as e:
                if e.response.status_code != 404:
                    raise
                costlies[COSTLY_CANDIDATES] = []
            costlies.sync()

    if key == COSTLY_WORKS:
        # If we don't have the resulting works
        if not COSTLY_WORKS in costlies.keys():
            if args is None:
                raise ValueError("list of works names required to fill work cache")
            # populate the cache
            with DrsDbContextBase() as ctx:

                # args is a tuple - the first element is the list
                # Get the work ids
                costlies[COSTLY_WORKS] = [WorkBit(x.workId, x.WorkName,) for x in [ctx.get_or_create_work(y) for y in args[0]]]

                logging.debug(f" Created {len(costlies[COSTLY_WORKS])} works")
                # Clear out any existing volumes - we're going to replace them all
                costlies[COSTLY_VOLUMES] = []
                costlies.sync()

                # we need to create the volumes when works are refreshed
                # Get the volumes for each work

                volumes: [int]
                for work_tuple in costlies[COSTLY_WORKS]:
                    swv = get_volumes_for_works(work_tuple)
                    vols = ctx.session.scalars(swv).all()
                    [costlies[COSTLY_VOLUMES].append(cv.volumeId) for cv in vols]
                costlies.sync()
                logging.debug(f" Created {len(costlies[COSTLY_VOLUMES])} volumes")

    # COSTLY_VOLUMES is built by COSTLY_WORKS
    return costlies[key]


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
    return costly_resources(COSTLY_CANDIDATES)


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
    return costly_resources(COSTLY_WORKS, work_elems)


def gb_project_load(member_ids: [str], project_name: str, project_desc: str, member_type: str):
    """
    Defines the GB Metadata project
    :param member_ids:  keys of project contents
    :param project_name: short name
    :param project_desc: long description
    :param member_type: One of the values of MemberTypes.Name
    :return:
    """

    from sqlalchemy_get_or_create import get_or_create

    with DrsDbContextBase() as ctx:
        ptype = select(ProjectTypes).where(ProjectTypes.project_type_name == "Distribution")
        pmtype = select(MemberTypes).where(MemberTypes.m_type == member_type)

        project_type = ctx.session.scalars(ptype).first()
        project_member_type = ctx.session.scalars(pmtype).first()

        defaults = {
            'project_type': project_type,
            'm_type': project_member_type
        }
        o, newly_made = get_or_create(ctx.session, Projects, defaults=defaults, name=project_name,
                                      description=project_desc)
        if newly_made:
            rstr = "Created"
        else:
            rstr = "Found"
        logging.info(f"{rstr} project {o}")

        not_started_member_state = ctx.session.scalars(
            select(MemberStates).where(MemberStates.m_state_name == "Not Started")).first()

        if member_type == "Work":
            for member_id in member_ids:
                ctx.session.add(
                    ProjectMembers(pm_work_id=member_id, project=o, project_member_state=not_started_member_state))
        else:
            if member_type == "Volume":
                for member_id in member_ids:
                    if member_type == "Volume":
                        ctx.session.add(
                            ProjectMembers(pm_volume_id=member_id, project=o, project_member_state=not_started_member_state))
            else:
                raise ValueError(f"project member type {member_type} is invalid. Valid values are \"Work\" or \"Volume\"")

        ctx.session.commit()


# Just invoke for testing
if __name__ == '__main__':
    werke = gb_transform(gb_proj_candidates())
    desc = """
    MARC record, one per work. Becomes the metadata for the content
    """
    gb_project_load(werke, "Google Books Metadata", desc, "Work")

    desc = """
    Volumes to upload, after their containing work's metadata is uploaded
    """
    gb_project_load(costly_resources(COSTLY_VOLUMES), "Google Books Contents", desc, "Volume")

