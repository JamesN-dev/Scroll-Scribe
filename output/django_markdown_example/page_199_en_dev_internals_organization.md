# Organization of the Django Project

## Principles

The Django Project is managed by a team of volunteers pursuing three goals:

- Driving the development of the Django web framework,
- Fostering the ecosystem of Django-related software,
- Leading the Django community in accordance with the values described in the [Django Code of Conduct](https://www.djangoproject.com/conduct/).

The Django Project isn’t a legal entity. The [Django Software Foundation](https://www.djangoproject.com/foundation/), a non-profit organization, handles financial and legal matters related to the Django Project. Other than that, the Django Software Foundation lets the Django Project manage the development of the Django framework, its ecosystem and its community.

## Mergers

### Role

[Mergers](https://www.djangoproject.com/foundation/teams/#mergers-team) are a small set of people who merge pull requests to the [Django Git repository](https://github.com/django/django/).

### Prerogatives

Mergers hold the following prerogatives:

- Merging any pull request which constitutes a [minor change](https://github.com/django/deps/blob/main/final/0010-new-governance.rst#terminology) (small enough not to require the use of the [DEP process](https://github.com/django/deps/blob/main/final/0001-dep-process.rst)). A Merger must not merge a change primarily authored by that Merger, unless the pull request has been approved by:
  - Another Merger,
  - A steering council member,
  - A member of the [triage & review team](https://www.djangoproject.com/foundation/teams/#triage-review-team), or
  - A member of the [security team](https://www.djangoproject.com/foundation/teams/#security-team).

- Initiating discussion of a minor change in the appropriate venue, and request that other Mergers refrain from merging it while discussion proceeds.

- Requesting a vote of the steering council regarding any minor change if, in the Merger’s opinion, discussion has failed to reach a consensus.

- Requesting a vote of the steering council when a [major change](https://github.com/django/deps/blob/main/final/0010-new-governance.rst#terminology) (significant enough to require the use of the [DEP process](https://github.com/django/deps/blob/main/final/0001-dep-process.rst)) reaches one of its implementation milestones and is intended to merge.

### Membership

[The steering council](https://www.djangoproject.com/foundation/teams/#steering-council-team) selects [Mergers](https://www.djangoproject.com/foundation/teams/#mergers-team) as necessary to maintain their number at a minimum of three, in order to spread the workload and avoid over-burdening or burning out any individual Merger. There is no upper limit to the number of Mergers.

It’s not a requirement that a Merger is also a Django Fellow, but the Django Software Foundation has the power to use funding of Fellow positions as a way to make the role of Merger sustainable.

The following restrictions apply to the role of Merger:

- A person must not simultaneously serve as a member of the steering council. If a Merger is elected to the steering council, they shall cease to be a Merger immediately upon taking up membership in the steering council.
- A person may serve in the roles of Releaser and Merger simultaneously.

The selection process, when a vacancy occurs or when the steering council deems it necessary to select additional persons for such a role, occur as follows:

- Any member in good standing of an appropriate discussion venue, or the Django Software Foundation board acting with the input of the DSF’s Fellowship committee, may suggest a person for consideration.
- The steering council considers the suggestions put forth, and then any member of the steering council formally nominates a candidate for the role.
- The steering council votes on nominees.

Mergers may resign their role at any time, but should endeavor to provide some advance notice in order to allow the selection of a replacement. Termination of the contract of a Django Fellow by the Django Software Foundation temporarily suspends that person’s Merger role until such time as the steering council can vote on their nomination.

Otherwise, a Merger may be removed by:

- Becoming disqualified due to election to the steering council.
- Becoming disqualified due to actions taken by the Code of Conduct committee of the Django Software Foundation.
- A vote of the steering council.

## Releasers

### Role

[Releasers](https://www.djangoproject.com/foundation/teams/#releasers-team) are a small set of people who have the authority to upload packaged releases of Django to the [Python Package Index](https://pypi.org/project/Django/) and to the [djangoproject.com](https://www.djangoproject.com/download/) website.

### Prerogatives

[Releasers](https://www.djangoproject.com/foundation/teams/#releasers-team) [build Django releases](../howto-release-django/) and upload them to the [Python Package Index](https://pypi.org/project/Django/) and to the [djangoproject.com](https://www.djangoproject.com/download/) website.

### Membership

[The steering council](https://www.djangoproject.com/foundation/teams/#steering-council-team) selects [Releasers](https://www.djangoproject.com/foundation/teams/#releasers-team) as necessary to maintain their number at a minimum of three, in order to spread the workload and avoid over-burdening or burning out any individual Releaser. There is no upper limit to the number of Releasers.

It’s not a requirement that a Releaser is also a Django Fellow, but the Django Software Foundation has the power to use funding of Fellow positions as a way to make the role of Releaser sustainable.

A person may serve in the roles of Releaser and Merger simultaneously.

The selection process, when a vacancy occurs or when the steering council deems it necessary to select additional persons for such a role, occur as follows:

- Any member in good standing of an appropriate discussion venue, or the Django Software Foundation board acting with the input of the DSF’s Fellowship committee, may suggest a person for consideration.
- The steering council considers the suggestions put forth, and then any member of the steering council formally nominates a candidate for the role.
- The steering council votes on nominees.

Releasers may resign their role at any time, but should endeavor to provide some advance notice in order to allow the selection of a replacement. Termination of the contract of a Django Fellow by the Django Software Foundation temporarily suspends that person’s Releaser role until such time as the steering council can vote on their nomination.

Otherwise, a Releaser may be removed by:

- Becoming disqualified due to actions taken by the Code of Conduct committee of the Django Software Foundation.
- A vote of the steering council.

## Steering Council

### Role

The steering council is a group of experienced contributors who:

- Provide oversight of Django’s development and release process,
- Assist in setting the direction of feature development and releases,
- Select Mergers and Releasers, and
- Have a tie-breaking vote when other decision-making processes fail.

Their main concern is to maintain the quality and stability of the Django Web Framework.

### Prerogatives

The steering council holds the following prerogatives:

- Making a binding decision regarding any question of a technical change to Django.
- Vetoing the merging of any particular piece of code into Django or ordering the reversion of any particular merge or commit.
- Announcing calls for proposals and ideas for the future technical direction of Django.
- Selecting and removing mergers and releasers.
- Participating in the removal of members of the steering council, when deemed appropriate.
- Calling elections of the steering council outside of those which are automatically triggered, at times when the steering council deems an election is appropriate.
- Participating in modifying Django’s governance (see [Changing the organization](#changing-the-organization)).
- Declining to vote on a matter the steering council feels is unripe for a binding decision, or which the steering council feels is outside the scope of its powers.
- Taking charge of the governance of other technical teams within the Django open-source project, and governing those teams accordingly.

### Membership

[The steering council](https://www.djangoproject.com/foundation/teams/#steering-council-team) is an elected group of five experienced contributors who demonstrate:

- A history of substantive contributions to Django or the Django ecosystem. This history must begin at least 18 months prior to the individual’s candidacy for the Steering Council, and include substantive contributions in at least two of these bullet points:
  - Code contributions to Django projects or major third-party packages in the Django ecosystem
  - Reviewing pull requests and/or triaging Django project tickets
  - Documentation, tutorials or blog posts
  - Discussions about Django on the Django Forum
  - Running Django-related events or user groups

- A history of engagement with the direction and future of Django. This does not need to be recent, but candidates who have not engaged in the past three years must still demonstrate an understanding of Django’s changes and direction within those three years.

A new council is elected after each release cycle of Django. The election process works as follows:

1. The steering council directs one of its members to notify the Secretary of the Django Software Foundation, in writing, of the triggering of the election, and the condition which triggered it. The Secretary posts to the appropriate venue – the [Django Forum](https://forum.djangoproject.com/) to announce the election and its timeline.
2. As soon as the election is announced, the [DSF Board](https://www.djangoproject.com/foundation/#board) begins a period of voter registration. All [individual members of the DSF](https://www.djangoproject.com/foundation/individual-members/) are automatically registered and need not explicitly register. All other persons who believe themselves eligible to vote, but who have not yet registered to vote, may make an application to the DSF Board for voting privileges. The voter registration form and roll of voters is maintained by the DSF Board. The DSF Board may challenge and reject the registration of voters it believes are registering in bad faith or who it believes have falsified their qualifications or are otherwise unqualified.
3. Registration of voters closes one week after the announcement of the election. At that point, registration of candidates begins. Any qualified person may register as a candidate. The candidate registration form and roster of candidates are maintained by the DSF Board, and candidates must provide evidence of their qualifications as part of registration. The DSF Board may challenge and reject the registration of candidates it believes do not meet the qualifications of members of the Steering Council, or who it believes are registering in bad faith.
4. Registration of candidates closes one week after it has opened. One week after registration of candidates closes, the Secretary of the DSF publishes the roster of candidates to the [Django Forum](https://forum.djangoproject.com/), and the election begins. The DSF Board provides a voting form accessible to registered voters, and is the custodian of the votes.
5. Voting is by secret ballot containing the roster of candidates, and any relevant materials regarding the candidates, in a randomized order. Each voter may vote for up to five candidates on the ballot.
6. The election concludes one week after it begins. The DSF Board then tallies the votes and produces a summary, including the total number of votes cast and the number received by each candidate. This summary is ratified by a majority vote of the DSF Board, then posted by the Secretary of the DSF to the [Django Forum](https://forum.djangoproject.com/). The five candidates with the highest vote totals immediately become the new steering council.

A member of the steering council may be removed by:

- Becoming disqualified due to actions taken by the Code of Conduct committee of the Django Software Foundation.
- Determining that they did not possess the qualifications of a member of the steering council. This determination must be made jointly by the other members of the steering council, and the [DSF Board](https://www.djangoproject.com/foundation/#board). A valid determination of ineligibility requires that all other members of the steering council and all members of the DSF Board vote who can vote on the issue (the affected person, if a DSF Board member, must not vote) vote “yes” on a motion that the person in question is ineligible.

## Changing the Organization

Changes to this document require the use of the [DEP process](https://github.com/django/deps/blob/main/final/0001-dep-process.rst), with modifications described in [DEP 0010](https://github.com/django/deps/blob/main/final/0010-new-governance.rst#changing-this-governance-process).