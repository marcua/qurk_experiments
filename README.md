# Qurk VLDB 2012 and 2013 experiments

This repository contains all of the code and as much as possible of the materials requires to recreate the "Human-powered Sorts and Joins" paper from VLDB 2012 and the "Counting with the Crowd" paper from VLDB 2013.

It is being released under a [CRAPL License](CRAPL-LICENSE.txt), and is neither representative of the authors' software engineering abilities nor organized in a way that the authors would be proud of today.  This README is organized into three sections:

* Setup required for both papers
* Steps required to trace throguh the footsteps of the authors on the VLDB 2012 paper
* Steps required to trace throguh the footsteps of the authors on the VLDB 2013 paper

Some notes and clarifications:

* Having stepped away from this codebase for two years and then returning to it to write a README on how to use it, it's clear that this work would best be repeated with the help of one of the authors.  Please contact Adam Marcus if you intend on using this codebase, and he will happily help you get started.
* Some files may remain in this repository from our SIGMOD 2011 demo of Qurk.  We've almost entirely sanitized this repository of the demo for the purposes of clarity, but if you see anything and are curious, we can retrieve the remainder of the files for you..


# Common setup notes
This section describes the required setup for both the VLDB 2012 and VLDB 2013 paper.

## Step 1: Ensure you have sufficient funds to run these experiments
Both papers cost on the order of $1000 worth of Mechanical Turk experimentation to run.  It will likely be cheaper to recreate the experiments if you make no mistakes, but reproducibility will likely require a significant investment.


## Step 2: Apply to your Institute Review Board (IRB)
If you are running these experiments from within academia, and are using government agency funds to run these experiments, you are endangering your school and lab's future funding if you do not apply to your Institite Review Board to perform experiments with human subjects.

Our application (to MIT's [COUHES](http://couhes.mit.edu/)) was pretty painless, but took a few back-and-forths and discussions of how we could get the equivalent of informed consent without a Turker being present and signing a physical form.  Before you can submit a similar application to your IRB, you will have to get human subjects training.  At an institution with a reasonable IRB, you should allocate about a month for training and approval.


## Step 3: Get the software hosted
The `qurkexp` directory is a Django application.  Read [qurkexp/wsgi/README](qurkexp/wsgi/README) for instructions on getting it running with WSGI.  Note that when we ran these experiments, MTurk displayed external HITs without an SSL requirement.  Some time in 2013, HITs hosted on external servers had to be available behind HTTPS.  We imagine there will be some changes required to get our experimental setup to work in this environment, and are happy to consult if you run into issues.

## Step 4: Configuring your MTurk credentials
The code in the `hitlayer` app contains all of the logic needed to generate HITs and poll for their assignments' completion.  You will probably get the most mileage out of this code.  The individual VLDB 2012/2013 apps call this code, but there are two important files you will make use of here:

  * `settings.py` contains your AWS credentials, as well as the flag for turning the AWS sandbox on and off
  * `killall.py` is the script you will likely call the most.  Say you create two simultaneous experiments, or accidentally generate $3000 worth of work when you meant to generate $30 worth of work.  Call `killall.py`.  _You should practice running this script before creating any experiments._


# VLDB 2012: Human-powered Sorts and Joins
All of the code for both our join- and our sort-based experiments can be found in the `join` Django app, inside of `qurkexp/join`.  There are many files in this directory.  Here is a tour of the most important ones:


Code that communicates with Mechanical Turk:

  * `generate_[batchpairs|comparisons|filters|pairs].py` Creates new experiments.  *Running these scripts will likely result in your spending money*.  The four scripts respectively are used to create [Naive/Smart batching joins|comparisons or ratings|filters for joins|simple joins] as described in the paper.  Whatever name you pick for your experiments will be used in later scripts to refer to that experiment.
  * `cron.py` is the daemon that will poll MTurk for completed HIT assignments and log Turker feedback.  Take note that there are several calls to `exit()` toward the bottom of the file.  Between blocks on `exit()`s is otherwise-unreachable code that we found helpful for both generating experiments and then polling for their completion, which makes it easier to walk away from the experiments as they run.
  * `movie_[batchpairs|comparisons|filters|results].py` contains all of the code for the end-to-end query in Section 5.
  * `latency.py` runs experiments and reports on experimental latency.

Calls external libraries:

  * `gal.py` is a Python driver for Ipeirotis et al.'s Get-Another-Label code (found in the `java/` subdirectory).  Given an experiment type and the name of several experiments (to combine), it will return the worker quality and most likely result according to the Get-Another-Label algorithm.  These results are reported as *QualityAdjust* in the paper.  

Backend code for munging MTurk data.  Doesn't communicate with Mechanical Turk:

  * `filter_results.py` and `filter_results_sample.py` contain the code necessary to evaluate Feature Filtering with or without sampling (Tables 2, 3, 4).
  * `hybrid.py` and `hybrid_[correlation|extrapolate].py` power the hybrid rate/sort algorithm in all of its variants.
  * `pair-datadump.py` dumps any of the join experiment data, broken down by worker response.
  * `pair-results.py` reports on the accuracy of the join experiments (Fig 3, Table 1) as well as the regression we ran in section 3.3.3.
  * `ranking-comparisons.py` compares different sort algorithms' accuracy (\Tau), as well as inter-rater agreement (\Kappa).  `run_names1` and `run_names2` specify which experiments (combined, if the list contains more than one experiment name) to utilize to generate a ranking, and then compares the two rankings. If `run_names1` contains `sortval` as the only member in its list, it will be used as a ground-truth comparison, which is how we measure \Tau. `ranking-comparisons-sampled.py` contains similar logic but for the sampled experiments in Figure 6.
  * `sort-datadump.py` dumps the contents of a comparison-based sort experiment.
  * `sort-results.py` runs similar logic to `ranking-comparisons.py`, but prints a less scientific measure of accuracy.  We used this to get examples of incorrect responses for both comparison-based and rating-based ranking.
  * `workers.py` contains all sorts of tricks for identifying overlapping workers and worker assignment histograms.




# VLDB 2013: Counting with the Crowd
All of the code for both our counting experiments can be found in the `estimation` Django app, inside of `qurkexp/estimation`. 

We got a little smarter about file and experiment organization here, so things are more sane than VLDB 2012:

* `datasets.py` contains a dictionary with the name of each dataset mapped onto the parameters of that dataset we'd like.  An example dataset is *shapes* where the user must estimate *fill color* where *red* takes up 10% of the dataset, and blue takes up 18%.  These datasets are sampled from the three core data sources: *shape* (the synthetic shapes we generated), *gtav* (the GTAV Face dataset), and *wgat* (the Who Gives A Tweet paper dataset).
* To generate the shapefiles for *shape*, we used `generate_shape.py`, though those files are included in this repository.
* To generate the faces in the GTAV face dataset, contact the authors of that dataset (this is at the GTAV authors' request).  When they give you the URL to download their dataset, set `GTAV_URL` in `gtav/fetch.py` and run the `fetch.py` script to revrieve the data.  Then run `generate_gtav.py` to instantiate the appropriate database models.
* To generate the WGAT dataset, contact us.  We worked with the authors of Who Gives a Tweet to retrieve their data, and can hopefully help you repeat that process.
* To materialize one of the datasets found in `datasets.py`, run `generate_sample.py dataset_name`.
* The experiments we ran can be found in `runs.py`.  After setting parameters for a run/experiment, you can instantiate it with `generate_run.py`.  *Running this script will likely result in your spending money*.
* `cron.py` Can be used to both call `generate_run.py` to create an experiment and to wait for/record HIT assignment responses.  It is generally saner than `cron.py` for the VLDB 2012 experiments.
* `endend_latency.py` plots the latency it takes to complete all of (most of) the HIT assignments for a task.  We don't use this plot in our paper.
* `interface_latency.py` plots a box-and-whiskers plot of the distribution of the number of seconds various Turkers took to finish various assignments.  This is Figure 5 in the paper.
* A bunch of figures are generated by using various techniques to estimate the fraction of items with some property for the various experiments.  This is done by `estimate_fractions.py`, and a bunch of examples can be found in `chartall.py`.  The output of `estimate_fractions.py` is a csv with estimated fractions from different runs/experiments and different estimation techniques (see lines 238-251 of `estimate_fractions.py` for a listing of these techniques.).
* The csv that `estimate_fractions.py` emits can then be processed by a few scripts to generate Figures 4 and 8 with `error_bars.py`.
* As a side effect of running (a poor engineering choice, yes) `estimate_fractions.py`, you also get convergence plots of the estimation techniques (Figure 6) and confidence interval width plots (Figure 7 and 9).
* The Sybil attach simulation is donein `sybil.py`, which emits a csv that can be consumed by `sybil_plot.py` (Figures 10 and 11).