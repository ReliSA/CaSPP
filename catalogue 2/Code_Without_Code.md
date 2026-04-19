[Home](../README.md) > [Catalogue](../Patterns_catalogue.md) > Code Without Code

# Code Without Code

## [Classification](facets/facets.md)

- [Category](facets/categories/categories.md):
- [Form](facets/forms/forms.md): [Artifact](facets/categories/Artifact.md)
- [Methodology](facets/methodologies/methodologies.md): [General](facets/methodologies/General.md)
- [Mode](facets/modes/modes.md): [General](facets/modes/General.md)
- [Primary perspective](facets/perspectives/perspectives.md): [Teacher](facets/perspectives/Teacher.md)
- [Stage](facets/stages/stages.md): [Supplementary](facets/stages/Supplementary.md)

## Context

As part of a low-level workshop, new computer science concepts, such as algorithms, should be taught to participants. The workshop is aimed at students without prior experience. The workshop focuses mainly on teaching coding-based concepts and is conducted by a computer science expert.

## Problem

Participants find it difficult to grasp and understand new concepts when they are presented and applied directly in code form. Additionally, code representation is not always linked to what actually happens. This can lead to frustration and can reduce the motivation of the participants to actively participate in the workshop.

## Forces

 - **Prior knowledge:** Participants have no or a varying level of prior knowledge in the field of computer science, for example knowledge of algorithms or programming languages.
 - **Complexity:** Different algorithms or concepts that are to be covered in the workshop cannot be conveyed in a beginnerfriendly way due to their complexity.
 - **Participant Preparation:** As this is a low-level workshop, no standardized preparation can be expected from the participants.
 - **Didactic quality:** The workshop holder may not be able to convey complex content in an understandable way.
 - **Attention span:** A short attention span can hinder learning, especially for new concepts.

## Solution

*Initially present coding-based concepts without code, but with physical, tangible objects instead.*

Instead of presenting new concepts directly in the form of code, they are first visualized using physical objects. However, this should not replace a code-based implementation, but rather serve as an additional level of the workshop. This is particularly useful as an introduction to a new topic [[MCN'99]](../References.md).

A possible implementation of the solution described in the context of a coding workshop could be, the creation of algorithms from scraps of paper. The individual pieces of paper represent various building blocks such as if statements, loops or variables. If, for example, an algorithm such as calculating an age based on the year of birth is to be learned as part of the workshop, participants can focus on solving the algorithmic problem and experiment freely with the building blocks without being restricted by code or a compiler.

## Consequences

 - (+) The visualization of concepts through physical objects allows reducing the **complexity** of the workshop. A more tangible visualization increases the participants’ **engagement** [[MCN'99]](../References.md).
 - (+) Visualization through physical objects is **independent of programming languages** and their syntax.
 - (+) The **threshold for engagement** for participants with little or no prior knowledge is reduced, resulting in an increased **beginner-friendliness** [[MCN'99]](../References.md).
 - (+) A physical visual representation increases the **memorability** of new content.
 - (+) The physical nature allows an **explorative** discovery of new concepts.
 - (+) The initial exploration of a new concept in physical form reduces the required **transfer performance** to the codebased representation.
 - (+) As there is no real code or compiler, the additional **overhead and confusion of potential error messages** while trying to solve a problem is removed.
 - (+) The use of physical objects, instead of a computer, allows for a **change of media** in the workshop.
 - (-) The required **preparation**, especially for the initial workshop, increases.
 - (-) More **time** is needed within the workshop to convey content.
 - (-) Physical objects are difficult to use for participants with **motor impairments**.
 - (-) **Complex concepts** or algorithms cannot always be completely represented by physical objects
 - (-) Physical objects can be **distracting** from the actual content, as they can tempt participants to play around instead of focusing on the actual content.
 - (-) The **seriousness** of concepts can be lost. Especially for experienced participants, this can lead to boredom and the feeling of not learning anything.
 - (-) Excessive **degrees of freedom** with physical coding representations may lead participants to perform actions that are not feasible in actual code, potentially fostering misconceptions and hindering the transition to practical implementation.
 - (-) Participants are not always able to identify problems in their solution themselves, therefore **external validation** by a teacher is needed.

## Related Patterns

|Pattern|Relation type|Relation description|
|--|--|--|
|Building Materials [[MUN'17]](../References.md)|prerequisite|To enable participants to for example build algorithms in a paper-based form, building materials like paper or building bricks are required.|
|Prototyping [[IBA'11]](../References.md)|potential enabler|The reduce in Overhead through the abundance of real code syntax supports the exploration of a topic and can therefore be used to try out ideas in a first prototype.|
 
## Example(s) / Known Use(s)

 - *Coding Culture.* As part of the ”Coding Culture Oberberg” research project, a workshop was held with a focus on sorting algorithms. One of the goals was to teach the bubble sort algorithm. However, before this was presented in code-based form, it was visualized using toy bricks, which are shown in figure 1[^1]. First, participants were able to try out different sorting concepts by using toy bricks of different heights. For this purpose, the procedure of the bubble sorting algorithm was then visualized by the workshop holder using the toy bricks. Before this concept was then transferred to a codebased representation, the participants had time to reproduce the procedure with their own toy bricks.

## Notes 

![Multiple toy bricks with different heights to visualize sorting algorithms](https://github.com/ReliSA/STePSEnHECs-PaCt/blob/main/catalogue/facets/publications/ber24/Code_Without_Code.png "Multiple toy bricks with different heights to visualize sorting algorithms")

Figure 1: Multiple toy bricks with different heights to visualize sorting algorithms

## [Sources](../References.md)

[[BER'24]](facets/publications/ber24/ber24.md)

---

[^1]: A visual demonstration can be seen [here](https://th-koeln.sciebo.de/s/l3q4BJ5xdoyTI9T)
