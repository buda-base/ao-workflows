# Queries to get books that have not been uploaded

use drs;
select distinct job_step from GB_Content_Track;

# count 10101
select count(*) from pm_project_members pmm;

# count = 6246 pmms  where there is nothing in GCT
# Get the label
select V.label from pm_project_members pmm
left join GB_Content_Track GCT on GCT.volume_id = pmm.pm_volume_id
inner join pm_member_states pms on pms.id = pmm.pm_project_state_id
               inner join Volumes V on V.volumeId = pmm.pm_volume_id
where GCT.volume_id is null
and pmm.pm_volume_id is not null
and pms.m_state_name = 'Not started'
limit 10;


# count: 4003 in GCT where not in pmm
select count(*) from GB_Content_Track GCT
left join pm_project_members pmm on GCT.volume_id = pmm.pm_volume_id
where GCT.volume_id is not null
and pmm.pm_volume_id is null;
