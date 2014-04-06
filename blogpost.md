# This is a work in progress---blog post forthcoming

# Reproducibility in the age of Mechanical Turk: We’re not there yet

There's been increasing interest in the computer science research community in exploring the reproducibility of our research findings.  [One such project](http://reproducibility.cs.arizona.edu/) recently received quite a bit of attention for exploring the reproducibility of 613 papers in ACM conferences.  The effort hit close to home: hundreds of authors were named and shamed, including those of us behind the VLDB 2012 paper [Human-powered Sorts and Joins](http://marcua.net/papers/qurk-vldb2012.pdf), because we did not provide instructions to reproduce the experiments in our paper.  I'm personally grateful to Collberg et al. for their work: it started quite a bit of discussion, and in our particular scenario, resulted in us posting [the code and instructions for our VLDB 2012 and 2013 papers on github](https://github.com/marcua/qurk_experiments).

In cleaning up the code and writing up the instructions, I had some time to think through what reproducibility means for crowd computing.  Can we, as Collberg et al. suggest, hold crowd research to the following standard:

	Can a CS student build the software within 30 minutes, including finding and installing any dependent software and libraries, and without bothering the authors?

My current thinking is a strong no: <b>not only can crowd researchers not hold their work to this standard of reproducibility, but it would be irresponsible for our community to reach that goal</b>.

Reproducibility is a laudable goal for all sciences.  For computer science systems research, it makes a lot of sense.  Systems builders are in the business of designing abstractions, automating processes, and proving properties of the systems they build.  In general, these skills should lend themselves nicely to building standalone reproductions-in-a-box that make it easy to rerun the work of other researchers.

So why does throwing a crowd into the mix break things?  It's the humans.  Crowd research isn't pure computer science research.  Our work draws on social sciences like psychology and economics as much as it does on computer science, and as a result we have to draw on approaches and expectations that those communities set for themselves.  The good thing is that in figuring out an appropriate standard for reproducibility, we can borrow lessons from these more established communities, so the solutions do not need to be novel.

## How does crowd research break the laudable goal of reproducibility?

From here, I'll spell out what makes crowd research reproducibility hard.  It won't be a complete list, and I won't pose many solutions.  As a community, I hope we can have a larger discussion around these points to define our own standards for reproducibility.

<b>Cost</b>. Crowdsourcing is not unique in costing money to reproduce. Collberg et al. had a category for papers that required specialized hardware, which is notoriously costly to acquire, install, and administer. Even when the hardware isn't proprietary, costs can be prohibitive: some labs have horror stories of researchers that accidentally left too many Amazon EC2 machines running for several days, incurring bills in the tens of thousands of dollars.  Still, compared to responsibly spinning up a few tens of machines on EC2 for a few hours, crowdsourced workflows can bankrupt you in far less time.

Each of our VLDB papers cost a little more than $1000 to crank through including errors we made along the way, but our errors were nowhere near what they could have been.  Accidentally creating too many pairwise comparison tasks could have easily increased our costs by an order of magnitude in just a few hours.  Reproducing crowdsourced systems research requires an upfront cost in the platform you’re using, but it also requires a nontrivial budget.  This expense is not insurmountable in the way that replicating the recruiting strategy of a psychology experiment or a wetlab setup of a biology experiment might be, but it’s should at least make you wary to get up and running in a half hour.  Whereas providing researchers with a single script to reproduce all of your experiments would be great for most systems, providing a single executable that spends a thousand dollars in a few hours might be irresponsible.

<b>Investing in the IRB process</b>.  One of the warnings we put in our [reproducibility instructions](https://github.com/marcua/qurk_experiments) was that you’d be risking future government agency funding if you ran our experiments without seeking institutional review board approval to work with human subjects.  Getting human subjects training and experiment approval takes on the order of a month for good reason: asking humans to sort some images seems harmless, but researchers have a [history poor judgement](https://en.wikipedia.org/wiki/Unethical_human_experimentation_in_the_United_States) when it comes to running experiments on other people.  Working with your IRB is a great idea, but it’s another cost along the path to quick-and-dirty reproduction of crowdsourcing experiments.

<b>Data sharing limitations</b>.  We could save researchers interested in reproducing and improving on our work a lot of money if we released our worker traces, allowing other scientists to inspect the responses workers gave us when we sent tasks their way.  Other researchers could vet our analyses without having to incur the cost of crowdsourcing for themselves.

There are many benefits to such data sharing, but in releasing worker traces, you risk compromising worker anonymity.  Turker IDs, while opaque, [are not anonymous](http://crowdresearch.org/blog/?p=5177).  As the [AOL search log fiasco shows](https://en.wikipedia.org/wiki/AOL_search_data_scandal), even if we obscured identifiers further, it’s still possible to identify seemingly anonymous users from usage logs.  IRBs are pretty serious about protecting personally identifiable information. Our IRB application does not cover sharing our data for these reasons. This limitation, like the others, is not unsolvable, but it will require the community to come together to figure out best practices for keeping worker identities safe.

<b>Tiny details matter</b>. Crowdsourced workflows have people at their core.  Providing workers with slightly different instructions can result in drastically different results.  When a worker is confused, they might reach out to you and ask for clarification.  How do you control for variance in experimenter responses or worker confusion?  What if, instead of requiring informed consent on only the first page a worker sees as our IRB requested, your IRB asks you to display the agreement on every page?  These little differences matter with humans in the loop.  Separating the effects of these differences in experimental execution is important to understanding whether an experiment reproduced another lab’s results.

<b>Crowds change over time</b>.  When we ran our experiments for our VLDB 2012 paper, we followed the reasonably rigorous [CrowdDB](https://amplab.cs.berkeley.edu/publication/crowddb-answering-queries-with-crowdsourcing/) protocol for vetting our results.  We ran each experiment multiple times during the east coast business hours of different weekdays, trusting only experiments that we could reproduce ourselves.  This process helped eliminate some irreproducible results.  Several months later, [Eugene](http://sirrice.com) and I re-ran all of our experiments before the camera ready deadline.  No dice: some of the results had changed, and we had to remove some findings we were no longer confident in.  [As Mechanical Turk sees changing demographic patterns](https://www.ics.uci.edu/~jwross/pubs/RossEtAl-WhoAreTheCrowdworkers-altCHI2010.pdf), you can expect your results to change as the underlying crowd does.  These changes will only compound the noise that you will already see across different workers.  This is no excuse for avoiding reproducibility: every experimental field has to account for diverse sources of variance, but it makes me wary of the one-script-to-reproduce-them-all philosophy that you might expect of other areas of systems research.

<b>Platforms change over time</b>. Even after all of the work we put into documenting our experiments for future generations, they won’t run out of the box.  Between the time that we ran our experiments and the time we released the reproducibility code, Amazon added an SSL requirement for servers hosting external HITs.  This is a wonderful improvement as far as security goes, but underscores the fact that relying on an external marketplace for your experiments is one more factor to compound the traditional [bit rot](https://en.wikipedia.org/wiki/Software_rot) that software projects see.

<b>Industry-specific challenges</b>.  Our VLDB 2012 and 2013 research was performed solely in academia.  I've since moved to do crowdsourcing research and development [in industry](http://blog.locu.com/post/25389032496/the-locu-workflow-a-crawler-a-learner-and-a-crowd).  This new environment poses new challenges to reproducibility.  While most of the code powering machine learning and workflow design for crowd work in industry is proprietary, so is the crowd.  At Locu we've got a few hundred workers that we've established long-term relationships with, working with many crowd workers for over two years.  Open sourcing the code behind our tools is one thing, but imagining other researchers bootstrapping the relationships and workflows we've developed for the purposes of reproducibility is near impossible.  Still, I believe industry has a lot to contribute to discussions around crowd-powered systems: the mechanism design, incentives, models, and interfaces we develop are of value to the larger community.  If industry is going to contribute to the discussion, we'll have to work through some tradeoffs, including less-than-randomized evaluations, not-fully-reproducible conclusions, and as a result, more contributions to engineering than to science.

As crowd research matures, it will be important for us to ask what reproducibility means to our community.  The answer will look pretty different from that of other areas of computer science.  What are your thoughts?