# FAQ: Contributing Code

## How Can I Get Started Contributing Code to Django?

Thanks for asking! We’ve written an entire document devoted to this question. It’s titled [Contributing to Django](https://docs.djangoproject.com/en/5.2/internals/contributing/).

## I Submitted a Bug Fix Several Weeks Ago. Why Are You Ignoring My Contribution?

Don’t worry: We’re not ignoring you!

It’s important to understand there is a difference between “a ticket is being ignored” and “a ticket has not been attended to yet.” Django’s ticket system contains hundreds of open tickets, of various degrees of impact on end-user functionality, and Django’s developers have to review and prioritize.

On top of that: the people who work on Django are all volunteers. As a result, the amount of time that we have to work on the framework is limited and will vary from week to week depending on our spare time. If we’re busy, we may not be able to spend as much time on Django as we might want.

The best way to make sure tickets do not get hung up on the way to checkin is to make it dead easy, even for someone who may not be intimately familiar with that area of the code, to understand the problem and verify the fix:

- Are there clear instructions on how to reproduce the bug? If this touches a dependency (such as Pillow), a contrib module, or a specific database, are those instructions clear enough even for someone not familiar with it?
- If there are several branches linked to the ticket, is it clear what each one does, which ones can be ignored and which matter?
- Does the change include a unit test? If not, is there a very clear explanation why not? A test expresses succinctly what the problem is, and shows that the branch actually fixes it.

If your contribution is not suitable for inclusion in Django, we won’t ignore it – we’ll close the ticket. So if your ticket is still open, it doesn’t mean we’re ignoring you; it just means we haven’t had time to look at it yet.

## When and How Might I Remind the Team of a Change I Care About?

A polite, well-timed message in the forum/branch is one way to get attention. To determine the right time, you need to keep an eye on the schedule. If you post your message right before a release deadline, you’re not likely to get the sort of attention you require.

Gentle reminders in the `#contributing-getting-started` channel in the [Django Discord server](https://chat.djangoproject.com) can work.

Another way to get traction is to pull several related tickets together. When someone sits down to review a bug in an area they haven’t touched for a while, it can take a few minutes to remember all the fine details of how that area of code works. If you collect several minor bug fixes together into a similarly themed group, you make an attractive target, as the cost of coming up to speed on an area of code can be spread over multiple tickets.

Please refrain from emailing anyone personally or repeatedly raising the same issue over and over again. This sort of behavior will not gain you any additional attention – certainly not the attention that you need in order to get your issue addressed.

## But I’ve Reminded You Several Times and You Keep Ignoring My Contribution!

Seriously - we’re not ignoring you. If your contribution is not suitable for inclusion in Django, we will close the ticket. For all the other tickets, we need to prioritize our efforts, which means that some tickets will be addressed before others.

One of the criteria that is used to prioritize bug fixes is the number of people that will likely be affected by a given bug. Bugs that have the potential to affect many people will generally get priority over those that are edge cases.

Another reason that a bug might be ignored for a while is if the bug is a symptom of a larger problem. While we can spend time writing, testing and applying lots of little changes, sometimes the right solution is to rebuild. If a rebuild or refactor of a particular component has been proposed or is underway, you may find that bugs affecting that component will not get as much attention. Again, this is a matter of prioritizing scarce resources. By concentrating on the rebuild, we can close all the little bugs at once, and hopefully prevent other little bugs from appearing in the future.

Whatever the reason, please keep in mind that while you may hit a particular bug regularly, it doesn’t necessarily follow that every single Django user will hit the same bug. Different users use Django in different ways, stressing different parts of the code under different conditions. When we evaluate the relative priorities, we are generally trying to consider the needs of the entire community, instead of prioritizing the impact on one particular user. This doesn’t mean that we think your problem is unimportant – just that in the limited time we have available, we will always err on the side of making 10 people happy rather than making a single person happy.

## I’m Sure My Ticket Is Absolutely 100% Perfect, Can I Mark It as “Ready For Checkin” Myself?

Sorry, no. It’s always better to get another set of eyes on a ticket. If you’re having trouble getting that second set of eyes, see questions above.