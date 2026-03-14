# Initial Project Directives

Date: February 22, 2026
Project: Critters (Working Title)

## Original Requirements Prompt

The following text is the raw directive provided at the start of the project to guide all future development and agent behavior:

Critters is a creature collector incremental game with a focus on exploration, building, and simulation. Explore the hand crafted world to find resources and secrets. Build a home. Watch your critters grow!

I think that blurb would be a good first introduction to most players. It’s what I imagine putting on the Steam front page, if I were ever to release this game. Not likely in this form, but it’s a good guiding principle to understand the features and player motivation.

Windows 11 is a fine setup for now. I don’t think I really need to use the WSL though. It’s just adding more complexity that I don’t need. I would like to use Git this time. I want to make sure agents tackle tasks as new branches and then merge those branches back into mainline. That way it’s clear what the heck they did and it could be easier to revert if they introduce a bug. Commits are also an easy way to see what agents did before, so later other agents can read the commits to see what they did.

For this initial prototype, I want to use Python and typical/popular python libraries. That way it is easy to understand the code and update myself. Also I may want to port this to another language or even Godot someday. If I do, I want it to be relatively easy to migrate the logic. I think Python will be easy to convert, even if it’s not particularly portable as a language. The logic itself should be easily understandable.

Also we need to keep track of all dependencies, so we can make it easy to install required dependencies. It would be good to keep a “dependencies” doc with commands to run that will install all required dependencies if you clone this project on a new computer. Every time we import a new dependency, we should update that dependencies file. The README should refer to the dependencies file and say that we should keep it up to date.

I think /doc, /src, /tst, /config would be top level directories, and README should be top level as well. Usually I would say tst is not so important, but for an agent lead project, tests are critical.

I agree with a section about how to verify the work is done. Definitely I’ll want to include a task list and agents should be able to put up tasks off the task list. The agent should update the task to say in progress, create a new fit branch, then they do the task. Then run all tests. Then they should add tests to test the new feature run all tests again. Assuming it’s working as intended, merge with mainline, and update the task as completed.

## Core Philosophy

1. **Logic First**: Prioritize clear, modular simulation logic over engine-specific features.
1. **Auditability**: Git branches and commits are the map of the project's history.
1. **Reliability**: Tests are the primary verification method for AI-generated code.
1. **Clean** Dependencies: Never add a library without documenting the installation command.