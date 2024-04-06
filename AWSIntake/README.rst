=========================
Configure AWS resources
=========================

This python module declares json to configure the AWS resources used by this project.
**It is highly desirable to source control the configuration - it keeps us from hunting around in the AWS console.**

On the other hand, we should develop the skill of using the AWS CLI to pull down existing configurations, so they
can be rebuilt or modified here. Just being careful of credentials.