from filter_results import *
import random
import numpy as np

def feature_fleiss(test_name, tfcs):
    features = Feature.objects.filter(featureexperiment__run_name = test_name).order_by('order')
    feature_matrices = {}
    for f in features:
        values = FeatureVal.objects.filter(feature = f).order_by('order')
        value_labels = [v.name for v in values]
        feature_matrices[f.name] = filter(lambda x: x != None, [fleiss_category_counts(c, f, value_labels) for c in tfcs])
    return [(f, computeKappa(feature_matrices[f.name])) for f in features]


# def celeb_feature_counts(celeb):
#     fras = FeatureRespAns.objects.filter(fr__celeb = celeb)
#     cd = {}
#     for fra in fras:
#         fn = fra.feature.name
#         vn = fra.val.name
#         feat = cd.get(fn, {})
#         vc = feat.get(vn, 0)
#         feat[vn] = vc + 1
#         cd[fn] = feat
#     return cd

# # batched

# metas = FeatureRespMeta.objects.filter(celeb__experiment__run_name=test_name)
# random.shuffle(metas)[:sample_size]
# for meta in metas:
    
        

if __name__ == "__main__":
    random.seed(0)
    tests = ["realfilters-batch-1",
             "realfilters-batch-4",
             "realfilters-nobatch-2",
             "realfilters-nobatch-5"]
             

    for test in tests:
        tfcs = FeatureCeleb.objects.filter(experiment__run_name = test)
        tfcs = [x for x in tfcs]

        res = {}
        sizes = []
        for sample_size in [15, 30, 45, 60]:
            sizes.append(sample_size)
        
            tmp = {}
            for i in xrange(50):
                idxs = range(len(tfcs))
                random.shuffle(idxs)
                sampledtfcs = map(lambda idx: tfcs[idx], idxs[:sample_size])
                tfs = dict(((c.cid, c.image_set), get_feature_dict(c)) for c in sampledtfcs)
                fkappapairs = feature_fleiss(test, sampledtfcs)

                for f, kappa in fkappapairs:
                    if f.name not in tmp:
                        tmp[f.name] =  []
                    tmp[f.name].append(kappa)
            
            for name, kappas in tmp.items():
                if name not in res: res[name] = []
                res[name].append((np.mean(kappas), np.std(kappas)))

        sizes = map(lambda x: "% 6d" % x,sizes)
        sizes.insert(0, '\t')
        print "AVG Run %s" % test
        
        print '\t'.join(sizes)
        for name, vals in res.items():
            avgs = [x[0] for x in vals]
            stds = [x[1] for x in vals]
            avgs = map(lambda x: "% 6f" % x,avgs)
            avgs.insert(0, name.split()[0])
            print '\t'.join(map(str,avgs))

        print "STD Run %s" % test
        print '\t'.join(sizes)
        for name, vals in res.items():
            avgs = [x[0] for x in vals]
            stds = [x[1] for x in vals]
            stds = map(lambda x: "% 6f" % x,stds)
            stds.insert(0, name.split()[0])
            print '\t'.join(map(str,stds))

        # print "MAGIC NUM Run %s" % test
        # for name, vals in res.items():
        #     perfect = vals[-1]
        #     magics = [(val[0] - perfect[0]) / val[1]   for val in vals]
        #     magics = map(lambda x: "% 6f" % x,magics)
        #     magics.insert(0, name.split()[0])
        #     print '\t'.join(map(str,magics))
