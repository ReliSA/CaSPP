[Home](../README.md) > [Catalogue](../Patterns_catalogue.md) > Team's Choice

# Team's Choice

## Also Known As

Team Chooses Topic

## [Classification](facets/facets.md)

- [Category](facets/categories/categories.md): 
- [Form](facets/forms/forms.md): [Activity](facets/categories/Activity.md)
- [Methodology](facets/methodologies/methodologies.md): [General](facets/methodologies/General.md)
- [Mode](facets/modes/modes.md): [General](facets/modes/General.md)
- [Primary perspective](facets/perspectives/perspectives.md): [Teacher](facets/perspectives/Teacher.md)
- [Stage](facets/stages/stages.md): [Team and Project Setup](facets/categories/Team_and_Project_Setup.md)

## Synopsis (optional)

How to pair up the teams with the project topics? Curate a selection of project topics, but account for the teams' preferences when assigning them.

## Context

We are running or planning to establish a (at least) semester-long university course on software engineering with collaborative student projects and including some aspects or the entire process of agile development. The goal being to provide learning by experience of agile principles and practices as well as general project management skills. No prior knowledge or experience of the students in these domains is assumed.

We have the students grouped into teams. We also have the curated list of feasible topics satisfying all the criteria for the projects.

## Problem

The best situation is a team working on a project their are enthusiastic about and qualified for. How to find the best fit when assigning the assembled teams to the gathered project topics?

## Forces

 - Having all students work on topics that are consistent in terms of difficulty helps with evaluation, enabling comparable evaluation criteria.
 - The topics the students work on should be adequate for the course, in terms of scope, complexity, number of features, and tech stack.
 - Feeling motivated helps students bring out their best work, but extrinsic motivation (such as that fuelled by a good grade) is not enough; intrinsic motivation ([[DEC'12]](../References.md)) (related to personal development and attachment to the work in progress) is paramount in a software project ([[BEE'08]](../References.md)).
 - The staff is not equipped to judge the teams' preferences, confidence, ambitions and experiences with different technologies without adequate information

## Solution

**Curate the selection of project topics, but take into account the preferences of team members when assigning them.**

There might be a discrepancy in pace of teams forming due to pre-existing relationships between students, or lack there of. To give all teams a level play field, with the opportunity for them to go through the team forming process ([[TUC'77]](../References.md)), the task of choosing a project topic ought to not be immediate. Teams should have time (depending on the course calendar, two or three weeks at the course's beginning or even before its start) to assess their options and make the choice they feel is best.

Regardless of the origin of the project topics, students should have a say on which topic they will be working on during the semester.

## Implementation

One avenue of implementing this is by letting students propose the topics for their own projects. With adequate guidance on the professor's part, students can come up with a topic they are invested in and that also meets the course's learning objectives.

Another way is to prepare a pool of topics and letting students pick from it. These topics can be internally proposed, by the professors, or externally, by outside organisations and customers. This can give the professors more control over the consistency between different topics, while giving students agency on their work.

A hybrid option is students bringing topics from their own contacts gained through previous studies, participation in research, personal relationships with people in the industry, or jobs they might already have.

An obvious final option is the course allowing for any mixture of all of the above, e.g., having a prepared pool of topics as a default, but allowing (or even encouraging) students to bring or come up with their own proposals. 

## Consequences

 - (+) Being able to have a say in what they will work on helps with students' sense of ownership, commitment and buy-in.
 - (-) Giving the teams a choice about their topics requires some care. In an instance where students propose their topics, they may end up with contrasts between teams, with some topics being more complex or wider in scope than others. This can make it harder to evaluate the students' work due to the different playing fields.
 - (-) If timeline does not allow for properly detailed topic assessments. If the description of a topic is to surface-level, short or vague, it can lead to mismatch between mismatch of expectations and reality in either direction on the students' or teachers' part. For example, the topic can appear easy to students and turn up to be overly challenging for their experience level. Or the topic (no matter its source) can be assessed as complex enough by the staff when its significant portion can be easily addressed by a free, third-party solution, thus drastically cutting the effort needed for the overall product.

## Related Patterns

|Pattern|Relation type|Relation description|
|--|--|--|
|[Smaller Project Scope](Smaller_Project_Scope.md)|facilitates, as students can better understand the point of the project, as well as compare between topics||
|[Self-Assembling Teams](Self-Assembling_Teams.md)|facilitates, as students will have a stronger familiarity and team identity that can lead to a more confident and appropriate topic choice||
|[Non-Essential Project](Non-Essential_Project.md)|precedes||
 
## Example(s) / Known Use(s)

 - [Advanced Software Engineerng](https://portal.zcu.cz/portal/studium/prohlizeni.html?pc_pagenavigationalstate=AAAAAQAGNjY0ODM5EwEAAAABAAhzdGF0ZUtleQAAAAEAFC05MjIzMzcyMDM2ODU0NzY3NTM1AAAAAA**#prohlizeniSearchResult), [Team Software Project](https://portal.zcu.cz/portal/studium/prohlizeni.html?pc_pagenavigationalstate=AAAAAQAGNjY0ODM5EwEAAAABAAhzdGF0ZUtleQAAAAEAFC05MjIzMzcyMDM2ODU0NzY3NTMzAAAAAA**#prohlizeniSearchResult) - A "call for topics" is sent out to both the industrial partners and internal organizational units of the university by the course staff well in advance (i.e., before the semester in which the course is taught starts). The gathered topics are screened for complexity, estimated scope [Smaller Project Scope](Smaller_Project_Scope.md), educational value, technology, business criticality [Non-Essential Project](Non-Essential_Project.md), etc. The students are also allowed to bring their own topic proposals, but a customer from outside the team needs to be defined. The resulting set is published to the students and the teams can express their preferences. The staff then assigns the projects mainly on these, outside of collisions in preferences or a stark mismatch of the topic and team's profile (technology experience, etc.). 
 - [Software Engineering](https://sigarra.up.pt/feup/en/UCURR_GERAL.FICHA_UC_VIEW?pv_ocorrencia_id=541882) - The course’s teachers select a common, broad theme for the project topics. In previous years, student apps have been related to student life, and more recently to the [UN’s Sustainable Development Goals](https://sdgs.un.org/goals). Students then choose a specific topic within these broader themes and receive feedback from their teachers throughout the process.
 - [Team Project](https://www.cs.ubbcluj.ro/files/curricula/2025/syllabus/IE_sem5_MLE5012_en_dsuciu_2025_9414.pdf) - The project teams pick a topic proposed by industry specialists or they define the project topic themselves, while project's difficulty is assessed by and instructor to remain consistent across teams. Project topics are not imposed, as this would decrease motivation for implementing the project.
 - Sytem Engineering[^1] - Students are free to choose their own topic.

## [Sources](../References.md)

[[PIN'25]](facets/publications/pin25/pin25.md)

---

[^1]: a course formerly taught at Free University of Bozen-Bolzano
