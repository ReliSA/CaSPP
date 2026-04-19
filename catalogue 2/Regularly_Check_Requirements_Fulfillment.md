[Home](../README.md) > [Catalogue](../Patterns_catalogue.md) > Regularly Check Requirements Fulfillment

# Regularly Check Requirements Fulfillment

## [Classification](facets/facets.md)

- [Category](facets/categories/categories.md): [Process Tailoring](facets/categories/Process_Tailoring.md)
- [Form](facets/forms/forms.md): [Activity](facets/categories/Activity.md)
- [Methodology](facets/methodologies/methodologies.md): [General](facets/methodologies/General.md)
- [Mode](facets/modes/modes.md): [General](facets/modes/General.md)
- [Primary perspective](facets/perspectives/perspectives.md): [Team](facets/perspectives/Team.md)
- [Stage](facets/stages/stages.md): [Execution](facets/stages/Execution.md)

## Context

A group assignment is given to a group of students. The project consists of single or multiple deliverables and the quality requirements are determined, either by the teacher or the students. You are at the beginning, middle or final phase of the project.

## Problem

If the work products delivered on the date of the deadline are incomplete or not of sufficient quality regarding the defined requirements, then the grading of these products will be low.

## Forces

 - *Individual work.* The group assumes that finished tasks made by an individual group member are done properly according to the given requirements. Because of this assumption, chances are the quality is not checked by the group and therefore the quality can be insufficient.
 - *Assumptions.* Students think their work products comply with the requirements, but did not actually check it.
 - *Ambition.* When students do not have the ambition to deliver high quality products, time spend on quality will possibly be low.
 - *Unseen Events.* During most group assignment events occur which stalls the progress of the assignment or the requirements changes. These events could lead to more work, which in consequence often leads to less time for quality checks.

## Solution

Determine for each deliverable how you can test and check the quality requirement on a regular base. Plan the time required for testing in your schedule.

## Implementation

Often the students work on an assignment, but they do not, or too little, check the deliverables against the defined criteria. This will result in lower quality products and in lower grading. By [START IMMEDIATELY](Start_Immediately.md) on the assignment and by [MANAGE THE PROJECT](Manage_The_Project.md) you should try to find some time for testing or checking your deliverables on a regular base.

For each quality requirement you need to find a way to test the deliverables. Like for instance build unit tests for your software, setup a continuous integration tool, make a software test document to write down your test results, arrange a user test with fellow classmates etc. Find out how much time your testing techniques take and consider how much time you want to spend on testing, because a 100 test cases in unit tests will take more time to develop than 15. If you do not aim for high quality products, you should reconsider about what your quality requirements are going to be.

Checking the quality of your deliverables on a regular base allows you to respond to requirement changes or errors in your product in an early stage. This will give you the possibility to adjust your planning and improve the quality.

You could also prevent a decrease in the quality of your deliverables, by [SPREAD TASK APPROPRIATELY](Spread_Tasks_Appropriately.md). Appropriately divided task will give you more time to check the quality. Let team members give feedback on each others work, because four eyes see more than two. Also tasks assigned to group members who have a high moving force to complete the task given to them will sometimes put up more effort to enhance the quality of the working product. Also it is advisable to [USE A STYLEGUIDE](Use_a_Styleguide.md) and [CENTRALIZE WORK PRODUCT MANAGEMENT](Centralize_Work_Product_Management.md) to prevent inconsistencies among the work products.

## Consequences

## Related Patterns

|Pattern|Relation type|Relation description|
|--|--|--|
|[Centralize Work Product Management](Centralize_Work_Product_Management.md)|complements|to prevent inconsistencies among the work products|
|[Manage The Project](Manage_The_Project.md)|part of|means to find some time for testing or checking deliverables on a regular base|
|[Spread Tasks Appropriately](Spread_Tasks_Appropriately.md)|facilitated by|prevents a decrease in the quality|
|[Start Immediately](Start_Immediately.md)|facilitated by|means to find some time for testing or checking deliverables on a regular base|
|[Use a Styleguide](Use_a_Styleguide.md)|complements|to prevent inconsistencies among the work products|
 
## Example(s) / Known Use(s)

 - An assignment was given to a group of students. During the initial evaluation it appears that the current working products did not met the defined requirements. This resulted in a low grading of the initial evaluation.
 - After the initial evaluation took place, they adjusted the planning so, that they could regularly check the quality of the products and solve any dissimilarity between the working products and the defined criteria. Each developer made unit tests before he started on a new feature. They also installed Jenkins to automate testing and building. In that way they could continuously test, build and control their code.
 - The students used SCRUM to directly distribute the changes each day, but also gave a group member the role as a tester. The tester was responsible to find the dissimilarity between deliverables and the requirements. Also they assigned the role of a team administrator to a group member to prevent inconsistency in the versions of the work products. This eventually resulted in a very high grading at the second evaluation.

## [Sources](../References.md)

[[COR'13]](facets/publications/cor13/cor13.md) 
