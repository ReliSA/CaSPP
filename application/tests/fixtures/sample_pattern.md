[Home](../README.md) > [Catalogue](../Patterns_catalogue.md) > Sample Pattern

# Sample Pattern

## Also Known As

Alias Name One, Alias Name Two

## [Classification](facets/facets.md)

- [Category](facets/categories/categories.md): [Guidance](facets/categories/Guidance.md)
- [Form](facets/forms/forms.md): [Activity](facets/forms/Activity.md)
- [Methodology](facets/methodologies/methodologies.md): [Agile](facets/methodologies/Agile.md)
- [Mode](facets/modes/modes.md): [General](facets/modes/General.md)
- [Primary perspective](facets/perspectives/perspectives.md): [Teacher](facets/perspectives/Teacher.md)
- [Stage](facets/stages/stages.md): [Execution](facets/stages/Execution.md)

## Context

Now the team has a grip on the assignment, defined tasks, and started working. The next step is reporting on progress. This context paragraph describes the situation in which the pattern applies and provides the reader with the background needed to understand the problem.

## Problem

As a teacher, how can you help students set up the right routines so that the team process is efficient and effective both regarding software production and the learning experience?

## Forces

 - **Reporting the status of work can be awkward for students**, especially for those who do not live up to expectations.
 - **Many students see reporting on work done as overhead:** it feels to them as unnecessary bureaucracy.
 - (+) Transparent progress boosts team motivation and accountability.
 - (-) Overhead of daily reporting can slow down development if not managed well.

## Solution

The solution involves establishing regular, short stand-up meetings where every team member states their progress yesterday and their plans for today. See [Scrum guidelines](http://example.com/scrum) for the canonical format.

We derived the following tips for teachers:
 - Join the daily stand-up at least twice a week so that your attendance feels natural.
 - Establish a community of trust: remind students that making mistakes is part of learning.
 - First, be a fly on the wall and let students run the stand-up in their own way.

## Implementation

Expand on the specifics of applying the solution in practice.

## Consequences

 - (+) Short feedback loops help students see results of their work very soon.
 - (+) Team members commit to specific tasks, improving accountability.
 - (-) Students may feel surveilled if the teacher attends too frequently.

## Related Patterns

|Pattern|Relation type|Relation description|
|--|--|--|
|[Shallow Feedback Loops](Shallow_Feedback_Loops.md)|uses|This pattern depends on short feedback loops to be effective|
|[Non-Daily Scrum](Non-Daily_Scrum.md)|variant of|A variant for teams that do not meet every day|

## Example(s) / Known Use(s)

 - A software engineering course at a Dutch university adopted daily stand-ups and reported measurable improvements in sprint velocity after the first two weeks.
 - An agile bootcamp used this pattern and noted that students corrected their own estimation errors faster than in previous cohorts.

## Notes

![Sample tracking chart](images/tracking_chart.png "Figure 1: Tracking progress chart")

Figure 1: Tracking progress chart showing sprint burndown over time.

---

Table 1: Stand-up observation checklist

||Score|Explanation|
|--|--|--|
|Team members stand up in a circle|||
|Plan board is visible for all team members|||
|No vague status updates are spoken|||

## [Sources](../References.md)

[[JAC'22]](facets/publications/jac22/jac22.md)

---

[^1]: A sprint is a phase of a project (which lasts mostly 2-4 weeks) in which an increment is delivered to the customer.