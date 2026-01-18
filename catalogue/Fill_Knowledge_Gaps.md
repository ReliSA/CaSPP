[Home](../README.md) > [Catalogue](../Patterns_catalogue.md) > Fill Knowledge Gaps

# Fill Knowledge Gaps

## [Classification](facets/facets.md)

- [Category](facets/categories/categories.md): [Team Dynamics](facets/categories/Team_Dynamics.md)
- [Form](facets/forms/forms.md): [Activity](facets/categories/Activity.md)
- [Methodology](facets/methodologies/methodologies.md): [General](facets/methodologies/General.md)
- [Mode](facets/modes/modes.md): [General](facets/modes/General.md)
- [Primary perspective](facets/perspectives/perspectives.md): [Team](facets/perspectives/Team.md)
- [Stage](facets/stages/stages.md): [Initiation](facets/stages/Initiation.md)

## Context

The group assignment requires a certain level of knowledge from all group members so that they can fulfill their assigned tasks. This knowledge might be taught in additional courses or expected to be present. The group already did [SHARE EXPECTATIONS](Share_Expectations.md).

## Problem

One or more members of the group do not have sufficient knowledge needed for working on the tasks assigned to them and cannot contribute sufficiently to the assignment realization. This endangers the overall successful completion of the assignment.

## Forces

 - *Different Knowledge Levels.* As the backgrounds from the students differ, it is possible that some students have more knowledge on the assignment’s subject than other group members.
 - *Motivation.* The knowledge of the subject often is taught in other courses, this knowledge is also dependent on the motivation of the students regarding these other courses. If students are not motivated to gather this knowledge in the other course, they miss this knowledge in the group assignment too, even if their motivation there is higher.
 - *Missing Opportunity.* The design of a curriculum can sometimes lead to situations where students can follow courses and group assignments even if they haven’t passed courses which form the basis for the course at hand. If this is the case, then it’s hard for students to already have the required knowledge present.
 - *Individual Strengths.* Different persons have different strengths, either because of different experiences or different interests. Even if the knowledge and skills of some required techniques are present, their level might be diverging between different students.

## Solution

Identify the knowledge gaps and help the group members with acquiring the missing knowledge. Let them in the beginning of the assignment execute smaller tasks of the assignment which match their current knowledge status until they grasped all required knowledge.

## Implementation 

Make sure that it is clear where the knowledge gaps are, otherwise the first step is to identify these as soon as possible. It hereby helps to make a list of the main important things the students have to know for being able to realize the tasks assigned to them. Then this list can be used for finding the gaps.

After it is clear which gaps to fill, there are several ways of helping other team members to do so:

 - If none of the group members has sufficient knowledge, have one member taking the task of acquiring the knowledge — e.g. by doing some research — and then present it to and share it with the whole group (also known as peer teaching).
 - If at least one member has the knowledge, then share this knowledge by pairing the inexperienced with the experienced team members and have the apprentice learn from the master. Pair programming is a good example of how this is realized in software engineering.

In order to assure that while filling the gaps it still is possible for group members to work on the overall assignment, it might be helpful to consider to temporarily [SPREAD TASKS APPROPRIATELY](Spread_Tasks_Appropriately.md).

The knowledge of the group members with insufficient knowledge will increase, at least to an amount which is enough for being a valuable member of the group. However, if the members in question are not showing enough commitment, require an active participation from them and, if necessary, [GIVE A FIRST WARNING](Give_a_First_Warning.md).

Applying this pattern may cost extra time if assistance by members with sufficient knowledge is required. This can lead to general time problems, so make sure you still can [DELIVER HIGH QUALITY PRODUCTS](Deliver_High_Quality_Products.md).

## Consequences

## Related Patterns

|Pattern|Relation type|Relation description|
|--|--|--|
|[Clear Up Questions.md](Clear_Up_Questions.md)|can be caused by||
|[Deliver High Quality Products](Deliver_High_Quality_Products.md)|calls for|make sure you still can|
|[Give a First Warning](Give_a_First_Warning.md)|can lead to/can follow|apply if the members lacking requisite knowledge are not showing enough commitment, and required active participation does not help|
|[Keep Motivated](Keep_Motivated.md)|contributes to||
|[Share Expectations](Share_Expectations.md)|preceded by|expected part of pre-conditions/context|
|[Spread Tasks Appropriately](Spread_Tasks_Appropriately.md)|can lead to/can follow|might be helpful to consider|
 
## Example(s) / Known Use(s)

 - A team had to work on an assignment where they were required to design the software architecture of a semi-complex system. They decided to apply some architectural and design patterns for realizing the non-functional requirements of the system, as they were familiar with the application of patterns. One team member stated that he had only heard about design patterns, but did not know in detail what it is. This team member was then paired with a "pattern specialist", who put some extra effort into explaining the patterns to the team member while using them for designing the architecture of the system. The other team-member therefore got an explanation of the patterns, but also immediately saw their application and therefore understood patterns much better after a short period.

## [Sources](../References.md)

[[KOP'12]](facets/publications/kop12/kop12.md)
