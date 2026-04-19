[Home](../README.md) > [Catalogue](../Patterns_catalogue.md) >  Face their facts

#  Face their facts

## Also Known As

Student’s accountability

## [Classification](facets/facets.md)

- [Category](facets/categories/categories.md):
- [Form](facets/forms/forms.md): [Activity](facets/categories/Activity.md)
- [Methodology](facets/methodologies/methodologies.md): [General](facets/methodologies/General.md)
- [Mode](facets/modes/modes.md): [General](facets/modes/General.md)
- [Primary perspective](facets/perspectives/perspectives.md): [Teacher](facets/perspectives/Teacher.md)
- [Stage](facets/stages/stages.md): [Grading](facets/categories/Grading.md)

## Context

Of course not every contribution a student makes is worthwhile in the grading process. ’Just doing it’, or worse: ’just trying to do it’ is not enough. In an educational situation, there simply is a lot of trial and error. But errors can be worthwhile to learn from. Taking samples from the big pile of work and grading them would not be a wise strategy because that would not do right to those who actually performed well but whose work did not surface in the sample.

## Problem

How can you get your focus on the relevant contributions of every individual?

## Forces

 - **Students reporting skills are not always up to par.** Some write terrible texts and others can not distinguish main issues from side issues. This could still lead to doing a lot of detective work and numbers of uninteresting edits. Moreover, it is the students who have to prove they are worth the credits. As their teacher you ’just’ want to check if they were right.

## Solution

In this solution two options are given by which students can demonstrate and explain their contributions. Depending on what you want them to proof you could choose either one or both.
 - **Fact sheet.** For every learning outcome ask every individual student to provide 3 to 5 facts which help proof that they were up to the task. These facts should be presented in the form of a clickable link to the designated work in the tool stack. The student should present their work by linking to a specific diff, commit, comment or pull request, accompanied by a one sentence explanation. By browsing through this list you will be able to quickly form an impression about the quality and quantity of the student’s contributions. Table 1 gives an example of how this might look like. Mind that just one learning outcome, and just one fact per assessment criterion is presented.
 - **Vary your sample size.** As stated in the general solution: if you sense a student is worth the group grade, just take a small sample (e.g. one or two facts) from the fact sheet to confirm your ideas. Only if your ideas are rejected then: dive deeper and take some more samples. Your attention needs to go to those of whom you are not so sure. In the worst case scenario you will have to check on every provided fact.
 - **Report.** For those learning outcomes where craftsmanship is not clear right away by looking at their work/facts, ask the students to individually judge the quality of some artefacts, explain their contributions in terms of theoretical concepts (e.g. design decisions, the rationale for the applied techniques underpinning an advice) they used, and how they reflect on their own role and team work. If you do this orally, your questions will only be focused on the points you doubt about. If it is a written report you need to instruct the students beforehand what they should write about, and according to your observations you filter out the relevant elements to read.

## Consequences

 - (+) Students must do the work, this prevents the teachers from becoming detectives.
 - (+) Sometimes students write about things in their own or the group’s process which give you a better understanding of what happened.
 - (+) Although many students resist reflecting, it could certainly give them new insights such as: What actually is the core of their work going to be when they start working after graduation? Or: What means craftsmanship to them?
 - (-) Writing fact sheets and reports is time consuming for students.
 - (-) Despite the idea that that a fact sheet helps to sample, it is still a potential rabbit hole due to the links. Sometimes it is difficult to stop clicking through if links are provided and you are a bit curiously minded.
 - (-) If your feedback on artefacts during the project was too concise, students might just give you back your own feedback.
 - (-) Some students are very well able to produce misleadingly good ’sweet talk’.

## Related Patterns

|Pattern|Relation type|Relation description|
|--|--|--|
|[2+2 makes four eyes](2_2_makes_four_eyes.md)|parent|solution to a broader problem|
 
## Example(s) / Known Use(s)

## Notes

LEARNING OUTCOME- Implement and evaluate the design of a distributed, algorithmic complex, embedded system
|Assessment criterion|Subject|Explanation|Link to work|
|--|--|--|--|
|Contributes evenly to the implementation of the system, in terms of quantity, quality and complexity|Positioning Server code|I wrote a method for grouping particles|Jira task 4654, Pull Request 14|
|Monitors progress and usability of the implementation (code) and documentation and checks if this is and stays in line with design documentation|Stairs Detection research document|I reviewed the behavior tree part and removed some errors from it, especially...|Jira task 356, Pull Request 67|

Table 1: Example of some facts from a fact sheet for an embedded software project

## [Sources](../References.md)

[[JAC'24]](facets/publications/jac24/jac24.md)

