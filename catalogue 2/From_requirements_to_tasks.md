[Home](../README.md) > [Catalogue](../Patterns_catalogue.md) > From requirements to tasks

# From requirements to tasks

## [Classification](facets/facets.md)

- [Category](facets/categories/categories.md): [Guidance](facets/categories/Guidance.md)
- [Form](facets/forms/forms.md): [Activity](facets/categories/Activity.md)
- [Methodology](facets/methodologies/methodologies.md): [General](facets/methodologies/General.md)
- [Mode](facets/modes/modes.md): [General](facets/modes/General.md)
- [Primary perspective](facets/perspectives/perspectives.md): [Teacher](facets/perspectives/Teacher.md)
- [Stage](facets/stages/stages.md): [Execution](facets/stages/Execution.md)

## Context

For an IT professional, deriving tasks from requirements is not difficult when requirements are clear [COP'05](../References.md). They know how to scope tasks, oversee potential difficulties and risks, and take dependencies into account; all this is mostly driven by experience. Students require guidance in this process, as they cannot build upon experience. Translating requirements to concrete tasks with accurate estimates is highly challenging for them.

Students often do not get more specific than dividing every given feature into four subtasks:
 1. Specifying the requirements
 2. Writing the software design description
 3. Programming
 4. Testing

## Problem

As a teacher, how can you help students to get from requirements to concrete, realistic, well-scoped tasks?

## Forces

Students lack lots of experience. Lacking experience and tending to underestimate task difficulty and duration is a result of lacking knowledge in five areas: The problem space, i.e. the requirements. Students focus on happy flows and underestimate the importance of alternative paths.
 - ***The solution space***, i.e. the technological ecosystem, in which the software is realized, as well as the architectural style of the system. Students do not easily oversee the applicability of technologies to new situations. So, they tend to use framework X or programming language Y again because “in our last project it worked very well, and we lack experience with a new one”. Of course, this is not always the cleverest way to go, they should closely consider the pro’s and cons.
 - ***The capabilities and skills of the team.*** The team consists of students with different skill levels in different domains. Sometimes the self-declared specialist in framework X appears not to be so valuable; or the silent girl appears very skilled in Y. This makes planning extra difficult.
 - ***The difference/relation between requirements and tasks***[^1], is not always clear to students, which results in students thinking that a requirement as the unit of planning is well enough. If they consider the requirement as a task, they will not be able to oversee what needs to be done, in what sequence, and how long it will take altogether. Which of course could result easily in them disappointing the customer.
 - ***The tool stack is used to support the development process.*** Getting to know your tool stack, whether it supports the whole development process or just the planning process, costs time and some endurance, but will be rewarding in the end. As students tend to focus on the short term and underestimate the complexity of their projects, they do not understand the positive impact on their project if they use the tool stack properly.

## Solution

The solution aims at making the students aware of the different knowledge areas involved in a project, resulting in some hints for defining tasks that will help them perform easily. 
<ul>
    <li><i>Making students aware of knowledge areas.</i> <b>Requirements as a stable basis.</b> Typically, knowledge about the solution space and knowledge about the capabilities and skills of the team are more problematic, especially at the beginning of the project; thus, as a teacher, make sure that at least the requirements are clear to the students, that there is a shared understanding, and a thorough and specific description of the requirements. With all the uncertainties involved, the requirements form the only reliable fundament for the task definition process.
    
In our own projects, we like to use use-case descriptions accompanied by a domain model and user interface sketches. The more specific, the better. Towards the end of the study, non functional requirements, particularly quality attribute requirements become important, as well, but in the beginning, they are typically ignored to a great extent; the focus is on functionality. Be precise as a teacher, only specific descriptions require students to think intensively about the requirements, which in turn provides a clearer picture of what needs to be done.
    
Our solution here consists of direct instruction so that students experience success early in the process. Do not strive for perfection, but for continuous improvement. This is in-sync with theories on self-efficacy and motivation. The latter is a result of action, not a prerequisite for it [KIR'18](../References.md). 
    <ul>
        <li><b>Architecture and technological ecosystem.</b> When it comes to the technological ecosystem, let the students make their own decision, but advise them to choose from the known rather than from the unknown. Bring in your own experience and provide specific advice if you see the students struggle. Before the first task planning, let them build small prototypes, so they can get a better understanding of what needs to be done to implement the functionality. For a web application, such a prototype could consist of a small user-interface with a form, a piece of backend that serves the user interface, and a chunk of the datastore to persist data. Of course, this highly depends on the nature of the project. It is important to cover all parts of the envisioned architecture. 
        </li>
        <li><b>Knowledge and skills of the project team.</b> This is the hardest part and at the same time the most important part, as the project is meant to improve the knowledge and skills of the students. It is the reason the project is done in the first place. To support a good learning experience: 
        <ul>
            <li>Be patient! Anticipate mistakes in the first iteration. Provide a lot of support in the beginning and gradually settle back and observe in later iterations 
            </li>
            <li>In the beginning: regularly check on their task management when you visit the team. Just open random tasks and share what you see and how this affects them reaching their goals. Be strict: they need to do better every time you have a look. 
            </li>
        </ul>
        </li>
        <li><b>Support with the tool stack.</b> Software development projects usually make use of tool stacks to support the process. In the case of Scrum, tools are used to manage sprint and product backlogs, provide a Scrum board, a burndown chart, usually a git repository and the like. All this can be overwhelming and distract students from the core of the learning experience. The same goes for planning tools like MS Project, or collaboration tools like MS SharePoint. Thus, make sure to provide good and very concrete instructions on how to use the tools. At least provide a simple planning tool so that it is easy to track progress. Ideally, the university provides and manages the entire tool stack for them. 
        </li>
    </ul>
    </li>
    <li><i>Hints for good task definitions.</i> Like the division of the first customer’s meeting into two sessions, also divide your guidance sessions into two parts. Give the team a limited period to arrange tasks as described above. You could suggest them use planning poker as a start. YouTube provides lots of instructional movies. Tell them you are available for any questions. Consider their results as a baseline for iterating further.
    
After some time, get back to them and help improve the task definitions by: 
    <ul>
        <li><b>Specifying what you expect in a task definition.<b> In our case, we require them to specify: 
        <ul>
            <li>Preconditions: Which conditions must be met before someone can start executing the task? 
            </li>
            <li>Postconditions: What are the functional (and sometimes nonfunctional) requirements that must be met when the task is considered done? 
            </li>
            <li>Estimated time: Ideally not longer than 4 hours, as having 4 as a maximum means that a single student is capable of finishing at least one task per day. This enhances motivation and helps them to talk about something useful at the next stand-up meeting. 
            </li>
            <li>The requirement addressed, if applicable 
            </li>
        </ul>
        </li>
        <li><b>Asking the students to organize tasks per requirement<b> (main level) and let them formulate subtasks. In software engineering projects, we distinguish at least separate tasks for: 
        <ul>
            <li>Software design 
            </li>
            <li>Coding-tasks 
            </li>
            <li>Testing 
            </li>
        </ul>
        </li>
    </ul>
    </li>
</ul>

## Consequences

## Related Patterns

|Pattern|Relation type|Relation description|
|--|--|--|
 
## Example(s) / Known Use(s)

## Notes (optional) 

![From requirements to tasks](https://github.com/ReliSA/STePSEnHECs-PaCt/blob/main/catalogue/facets/publications/jac22/From_requirements_to_tasks.png "From requirements to tasks")

Figure 1: From requirements to tasks

## [Sources](../References.md)

[[JAC'22]](facets/publications/jac22/jac22.md)

---

[^1]: A requirement is what the customer wants, a wish. All activities necessary to provide for the wish are tasks. E.g. a requirement is “Please give me a birthday cake”. If the cake is not in the shelf already -which it is not in ICT- you need to define a sequence of smaller tasks to be able to meet the customers wish (choosing which recipe, buying ingredients, baking the cake, icing and delivering it).
