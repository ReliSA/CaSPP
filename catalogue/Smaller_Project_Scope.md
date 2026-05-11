[Home](../README.md) > [Catalogue](../Patterns_catalogue.md) > Smaller Project Scope

# Smaller Project Scope

## [Classification](facets/facets.md)

- [Category](facets/categories/categories.md):
- [Form](facets/forms/forms.md): [Activity](facets/categories/Activity.md)
- [Methodology](facets/methodologies/methodologies.md): [General](facets/methodologies/General.md)
- [Mode](facets/modes/modes.md): [General](facets/modes/General.md)
- [Primary perspective](facets/perspectives/perspectives.md): [Teacher](facets/perspectives/Teacher.md)
- [Stage](facets/stages/stages.md): [Team and Project Setup](facets/categories/Team_and_Project_Setup.md)

## Synopsis

How to efficiently teach the practices given the limited capacity of the course? Assign smaller, worthwhile projects accounting for the educational activities within and the team's capacity.

## Context

We are running or planning to establish a (at least) semester-long university course on software engineering with collaborative student projects and including some aspects or the entire process of agile development. The goal being to provide learning by experience of agile principles and practices as well as general project management skills. No prior knowledge or experience of the students in these domains is assumed.

## Problem

How to efficiently provide students with practical education on the process and practices while creating a worthwhile product given the limited time the students have as dictated among others by the credit volume of the course?

## Forces

 - The students do not work full time on the project, juggling it with their responsibilities from other parts of the course (lectures, exams; plus the overall spent time limitation on the course per the number of credits gained from passing), other courses, personal lives and, potentially, part-time jobs. Depending on how many credits the course is worth they may have more time, but there is no exclusivity on the students’ end.
 - Agile processes combine several moving parts, including ceremonies, practices, and principles, to name a few. Hands-on experience with these helps students see how everything fits, leading to better comprehension and a sense of being more than just theoretical stuff they need to recite for the exam.
 - Students should have something to work towards, and a project with a clear goal is a good way to keep them engaged. Even better if they can see a real-world benefit to a customer who validates their effort and results, rather than "yet another" artificial (purely) educational assignment which will only end up in a drawer forever.
 - Students may be hardwired from other courses that all that matters for the project is the quality of the end result, automatically ignoring the "whys and hows" to reach it reliably.

## Solution

**Assign smaller projects to students that can be of value while accounting for the team's size, the expected engagement from the course, and the educational activities within the project.**

When we, as educators, want to teach students about the mechanisms behind the processes they are working on, we should focus their attention at the mechanisms themselves. However, it is easy for students to not see the forest for the trees depending on their previous experiences in other courses, where the project's end result was all that mattered.

As such, in order to shift the students attention, educators can propose topics that are \emph{smaller} in scope but that still make for a coherent and well-thought out project.

With this, students should not be working fully at capacity, giving them room for agile ceremonies, other tasks (such as the ones that may be present for evaluation purposes but that don't advance development), and also giving them slack time. In a course where each student should have 80 hours of development time, they should be working on a 60-hour project.

This can be achieved, in the case of an externally-proposed topic, by giving students room to negotiate scaling down the scope of the topic. On the other hand, if the students are proposing their own topic, they can start small, having room to grow with the guidance of their professor.

## Consequences

 - (+) Having projects that are smaller in scope helps students to maintain a sustainable pace, helping them remain aligned with Agile principles. The sustainable pace assists in students not scrambling to get things done at the last minute, which together with a reduced workload gives students the room to be intentional about their actions and really take in the reasons behind what they are doing in the course of their projects.
 - (+) Smaller projects are also more easily and accurately grasped mentally. This can spark creativity, when students are given a choice to come up with their own project topics, or help assess the topics assigned or up for selection.
 - (-) A Smaller Project Scope can backfire and steer students the wrong way, downplaying what they need to work on for the project and resulting in poorer time management, which in turn leads the team to work at an unsustainable pace.

## Related Patterns

|Pattern|Relation type|Relation description|
|--|--|--|
|[Team Size Limitation](Team_Size_Limitation.md)|partial driver as the aggregate team capacity puts a limitation on the scope from the start||
|[Team's Choice](Teams_Choice.md)|facilitated through fostering better informed choices and either creativity (coming up with own topic) or comprehenssion and complexity assessment (if topic given)||
|[Non-Essential Project](Non-Essential_Project.md)|supported, as the customers rarely have proposals that are small enough for the courses, yet very important or business critical||
 
## Example(s) / Known Use(s)

 - [Advanced Software Engineerng](https://portal.zcu.cz/portal/studium/prohlizeni.html?pc_pagenavigationalstate=AAAAAQAGNjY0ODM5EwEAAAABAAhzdGF0ZUtleQAAAAEAFC05MjIzMzcyMDM2ODU0NzY3NTM1AAAAAA**#prohlizeniSearchResult), [Team Software Project](https://portal.zcu.cz/portal/studium/prohlizeni.html?pc_pagenavigationalstate=AAAAAQAGNjY0ODM5EwEAAAABAAhzdGF0ZUtleQAAAAEAFC05MjIzMzcyMDM2ODU0NzY3NTMzAAAAAA**#prohlizeniSearchResult) - Customers are informed by the course staff prior to topic submissions on the estimated scope of the projects, taking into account the administrative overhead the students have to apply in the projects [Higher Ceremony](Higher_Ceremony.md). They are also encouraged to submit topics that can be easily scaled up or down based on the specific project context (i.e., the varying number of team members). The topics are subsequently screened by the course staff in this regard to the best of their ability. The mentors are also ready to assist the teams to resolve a situation where the fact that the topic is significantly more/less complex than originally estimated is discovered during the project's execution. 
 - [Software Engineering](https://sigarra.up.pt/feup/en/UCURR_GERAL.FICHA_UC_VIEW?pv_ocorrencia_id=541882) - Teams are encouraged to keep their project topics simple with an easy-to-implement minimum viable product, with the option to grow in scope as the semester progresses and the team implements their initial view of the project.
 - [Team Project](https://www.cs.ubbcluj.ro/files/curricula/2025/syllabus/IE_sem5_MLE5012_en_dsuciu_2025_9414.pdf) - Uses teams of 8-10 students with the expected 50 hours spent per student per semester.
 - [Software Construction](https://www.fhnw.ch/plattformen/swc/) - Teams of 3 students work on a small, approx. 4K LOC, application.
 
## [Sources](../References.md)

[[PIN'25]](facets/publications/pin25/pin25.md)
