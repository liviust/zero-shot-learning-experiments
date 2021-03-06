import numpy as np
import optunity
import optunity.metrics

from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import average_precision_score
from sklearn.externals import joblib

from grid_attributes_functions import *

########################################
# ATTRIBUTES
########################################

# Speaker identity

# Male or not

# Bilabial or not

# Duration of word

# Head Pose Mean (3)

# Head Pose Range (3)

# LipreaderEncoder Features (64)

#############################################################
# LOAD BASICS
#############################################################

grid_basics = np.load('grid_basics.npz')

train_dirs = grid_basics['train_dirs']
train_word_numbers = grid_basics['train_word_numbers']
train_word_idx = grid_basics['train_word_idx']

val_dirs = grid_basics['val_dirs']
val_word_numbers = grid_basics['val_word_numbers']
val_word_idx = grid_basics['val_word_idx']

si1314_dirs = grid_basics['si131410_dirs']; si1314_dirs = si1314_dirs[:12000]
si1314_word_numbers = grid_basics['si131410_word_numbers']; si1314_word_numbers = si1314_word_numbers[:12000]
si1314_word_idx = grid_basics['si131410_word_idx']; si1314_word_idx = si1314_word_idx[:12000]

#############################################################
# LOAD ATTRIBUTES
#############################################################

train_grid_attributes = np.load('train_grid_attributes_matrix.npy')
val_grid_attributes = np.load('val_grid_attributes_matrix.npy')
si131410_grid_attributes = np.load('si131410_grid_attributes_matrix.npy'); si1314_grid_attributes = si131410_grid_attributes[:12000]

# Normalization
train_grid_attributes_peak_to_peak = train_grid_attributes.ptp(0)
train_grid_attributes_peak_to_peak[np.argwhere(train_grid_attributes_peak_to_peak == 0)] = 1
train_grid_attributes_norm = (train_grid_attributes - train_grid_attributes.min(0)) / train_grid_attributes_peak_to_peak
val_grid_attributes_peak_to_peak = val_grid_attributes.ptp(0)
val_grid_attributes_peak_to_peak[np.argwhere(val_grid_attributes_peak_to_peak == 0)] = 1
val_grid_attributes_norm = (val_grid_attributes - val_grid_attributes.min(0)) / val_grid_attributes_peak_to_peak
si1314_grid_attributes_peak_to_peak = si1314_grid_attributes.ptp(0)
si1314_grid_attributes_peak_to_peak[np.argwhere(si1314_grid_attributes_peak_to_peak == 0)] = 1
si1314_grid_attributes_norm = (si1314_grid_attributes - si1314_grid_attributes.min(0)) / si1314_grid_attributes_peak_to_peak

train_grid_attributes_norm = (train_grid_attributes - train_grid_attributes.min(0)) / train_grid_attributes.ptp(0)
val_grid_attributes_norm = (val_grid_attributes - val_grid_attributes.min(0)) / val_grid_attributes.ptp(0)
si1314_grid_attributes_norm = (si1314_grid_attributes - si1314_grid_attributes.min(0)) / si1314_grid_attributes.ptp(0); si1314_grid_attributes_norm[:, 1] = 1.

# Leave out the first three attributes
train_matrix = train_grid_attributes_norm[:, 3:]
val_matrix = val_grid_attributes_norm[:, 3:]
si1314_matrix = si1314_grid_attributes_norm[:, 3:]

# # Check correlation between attributes
# plt.imshow(np.abs(np.corrcoef(train_grid_attributes.T)), cmap='gray', clim=[0, 1]); plt.title("Attributes correlation"); plt.show()

# plt.imshow(np.abs(np.corrcoef(train_grid_attributes[:, :10].T)), cmap='gray', clim=[0, 1])
# plt.xticks(np.arange(10), ('Identity', 'Male', 'Bilabial', 'Duration', 'PoseX Mean', 'PoseY Mean', 'PoseZ Mean', 'PoseX Range', 'PoseY Range', 'PoseZ Range'), rotation=45)
# plt.yticks(np.arange(10), ('Identity', 'Male', 'Bilabial', 'Duration', 'PoseX Mean', 'PoseY Mean', 'PoseZ Mean', 'PoseX Range', 'PoseY Range', 'PoseZ Range'))
# plt.title("Attributes correlation")
# plt.show()

#############################################################
# LOAD CORRECT_OR_NOT
#############################################################

lipreader_preds_wordidx_and_correctorwrong = np.load('lipreader_preds_predWordIdx_correctOrNot.npz')

train_lipreader_preds_word_idx = lipreader_preds_wordidx_and_correctorwrong['train_lipreader_preds_word_idx']
val_lipreader_preds_word_idx = lipreader_preds_wordidx_and_correctorwrong['val_lipreader_preds_word_idx']
si1314_lipreader_preds_word_idx = lipreader_preds_wordidx_and_correctorwrong['si1314_lipreader_preds_word_idx']

train_lipreader_preds_correct_or_wrong = lipreader_preds_wordidx_and_correctorwrong['train_lipreader_preds_correct_or_wrong']
val_lipreader_preds_correct_or_wrong = lipreader_preds_wordidx_and_correctorwrong['val_lipreader_preds_correct_or_wrong']
si1314_lipreader_preds_correct_or_wrong = lipreader_preds_wordidx_and_correctorwrong['si1314_lipreader_preds_correct_or_wrong']

# >>> np.sum(train_lipreader_preds_correct_or_wrong)/len(train_lipreader_preds_correct_or_wrong)
# 0.92210520716983135
# >>> np.sum(val_lipreader_preds_correct_or_wrong)/len(val_lipreader_preds_correct_or_wrong)
# 0.92036242250834521
# >>> np.sum(si_lipreader_preds_correct_or_wrong)/len(si_lipreader_preds_correct_or_wrong)
# 0.38550000000000001

#############################################################
# LOAD LIPREADER PREDS
#############################################################

# lipreader_preds = np.load('lipreader_preds.npz')

train_lipreader_preds = lipreader_preds_wordidx_and_correctorwrong['train_lipreader_preds']
val_lipreader_preds = lipreader_preds_wordidx_and_correctorwrong['val_lipreader_preds']
si1314_lipreader_preds = lipreader_preds_wordidx_and_correctorwrong['si131410_lipreader_preds']; si1314_lipreader_preds = si1314_lipreader_preds[:12000]

#############################################################
# LOAD CRITIC PREDS
#############################################################

critic_preds = np.load('critic_preds.npz')

train_critic_preds = critic_preds['train_critic_preds']
val_critic_preds = critic_preds['val_critic_preds']
si1314_critic_preds = critic_preds['si1314_critic_preds']

#############################################################
# LIPREADER ROC
#############################################################

# Compute ROC
lipreader_train_fpr, lipreader_train_tpr, lipreader_train_roc_auc, \
        lipreader_val_fpr, lipreader_val_tpr, lipreader_val_roc_auc, \
        lipreader_si_fpr, lipreader_si_tpr, lipreader_si_roc_auc = \
    compute_ROC_grid_multiclass(train_word_idx, train_lipreader_preds,
        val_word_idx, val_lipreader_preds,
        si_word_idx, si_lipreader_preds,
        savePlot=True, showPlot=True,
        plot_title='Baseline ROC curve of lipreader')

np.savez('ROC_baseline_lipreader',
    lipreader_train_fpr=lipreader_train_fpr, lipreader_train_tpr=lipreader_train_tpr, lipreader_train_roc_auc=lipreader_train_roc_auc,
    lipreader_val_fpr=lipreader_val_fpr, lipreader_val_tpr=lipreader_val_tpr, lipreader_val_roc_auc=lipreader_val_roc_auc,
    lipreader_si_fpr=lipreader_si_fpr, lipreader_si_tpr=lipreader_si_tpr, lipreader_si_roc_auc=lipreader_si_roc_auc)
    # train_lipreader_OP_fpr=train_lipreader_OP_fpr, train_lipreader_OP_tpr=train_lipreader_OP_tpr,
    # val_lipreader_OP_fpr=val_lipreader_OP_fpr, val_lipreader_OP_tpr=val_lipreader_OP_tpr,
    # si_lipreader_OP_fpr=si_lipreader_OP_fpr, si_lipreader_OP_tpr=si_lipreader_OP_tpr)

#############################################################
# LIPREADER PR CURVE
#############################################################

train_lipreader_recall_OP, train_lipreader_precision_OP, train_lipreader_precision, train_lipreader_recall, train_lipreader_average_precision = \
    compute_grid_multiclass_PR_plot_curve(train_word_idx, train_lipreader_preds, train_lipreader_preds_word_idx, plotCurve=True)
# Recall_OP["micro"]: 0.92, Precision_OP["micro"]: 0.92
# Recall_OP["macro"]: 0.85, Precision_OP["macro"]: 0.87
# precision from sklearn at recall_OP["micro"]: 1.00
# Average precision score, micro-averaged over all classes: 0.98

val_lipreader_recall_OP, val_lipreader_precision_OP, val_lipreader_precision, val_lipreader_recall, val_lipreader_average_precision = \
    compute_grid_multiclass_PR_plot_curve(val_word_idx, val_lipreader_preds, val_lipreader_preds_word_idx, plotCurve=True)



si1314_lipreader_recall_OP, si1314_lipreader_precision_OP, si1314_lipreader_precision, si1314_lipreader_recall, si1314_lipreader_average_precision = \
    compute_grid_multiclass_PR_plot_curve(si1314_word_idx, si1314_lipreader_preds, si1314_lipreader_preds_word_idx, plotCurve=True)


#############################################################
# CRITIC PR CURVE
#############################################################

train_critic_recall_OP, train_critic_precision_OP, train_critic_precision, train_critic_recall, train_critic_average_precision = \
    compute_grid_singleclass_PR_plot_curve(train_lipreader_preds_correct_or_wrong, train_critic_preds, plotCurve=True)
# recall_OP: 0.64, precision_OP: 0.96
# precision from sklearn at recall_OP: 1.00
# Average precision-recall score: 0.97

val_critic_recall_OP, val_critic_precision_OP, val_critic_precision, val_critic_recall, val_critic_average_precision = \
    compute_grid_singleclass_PR_plot_curve(val_lipreader_preds_correct_or_wrong, val_critic_preds, plotCurve=True)
# recall_OP: 0.64, precision_OP: 0.96
# precision from sklearn at recall_OP: 1.00
# Average precision-recall score: 0.97

si1314_critic_recall_OP, si1314_critic_precision_OP, si1314_critic_precision, si1314_critic_recall, si1314_critic_average_precision = \
    compute_grid_singleclass_PR_plot_curve(si1314_lipreader_preds_correct_or_wrong, si1314_critic_preds, plotCurve=True)
# recall_OP: 0.64, precision_OP: 0.96
# precision from sklearn at recall_OP: 1.00
# Average precision-recall score: 0.97




#############################################################
# CRITIC ROC
#############################################################

# CONFUSION MATRIX, OPERATING POINT
# Train
train_critic_tn, train_critic_fp, train_critic_fn, train_critic_tp = confusion_matrix(train_lipreader_preds_correct_or_wrong, train_critic_preds > .5).ravel()
train_critic_OP_fpr = train_critic_fp/(train_critic_fp + train_critic_tn)
train_critic_OP_tpr = train_critic_tp/(train_critic_tp + train_critic_fn)
# Val
val_critic_tn, val_critic_fp, val_critic_fn, val_critic_tp = confusion_matrix(val_lipreader_preds_correct_or_wrong, val_critic_preds > .5).ravel()
val_critic_OP_fpr = val_critic_fp/(val_critic_fp + val_critic_tn)
val_critic_OP_tpr = val_critic_tp/(val_critic_tp + val_critic_fn)
# Si
si_critic_tn, si_critic_fp, si_critic_fn, si_critic_tp = confusion_matrix(si_lipreader_preds_correct_or_wrong, si_critic_preds > .5).ravel()
si_critic_OP_fpr = si_critic_fp/(si_critic_fp + si_critic_tn)
si_critic_OP_tpr = si_critic_tp/(si_critic_tp + si_critic_fn)

# Acc
# >>> (train_critic_tp + train_critic_tn)/(train_critic_tp + train_critic_fp + train_critic_fn + train_critic_tn)
# 0.64650816445933723
# >>> (val_critic_tp + val_critic_tn)/(val_critic_tp + val_critic_fp + val_critic_fn + val_critic_tn)
# 0.64854554124940389
# >>> (si_critic_tp + si_critic_tn)/(si_critic_tp + si_critic_fp + si_critic_fn + si_critic_tn)
# 0.6323333333333333

# # Compute ROC
# train_critic_fpr, train_critic_tpr, train_critic_thresholds, train_critic_roc_auc, \
#         val_critic_fpr, val_critic_tpr, val_critic_thresholds, val_critic_roc_auc, \
#         si_critic_fpr, si_critic_tpr, si_critic_thresholds, si_critic_roc_auc = \
#     compute_ROC_grid_singleclass(train_lipreader_preds_correct_or_wrong, train_critic_preds,
#         val_lipreader_preds_correct_or_wrong, val_critic_preds,
#         si_lipreader_preds_correct_or_wrong, si_critic_preds,
#         train_critic_OP_fpr, train_critic_OP_tpr,
#         val_critic_OP_fpr, val_critic_OP_tpr,
#         si_critic_OP_fpr, si_critic_OP_tpr,
#         savePlot=True, showPlot=True,
#         plot_title='ROC curve of C3DCritic')

# train_critic_roc_auc, val_critic_roc_auc, si_critic_roc_auc
# # (0.73482362164374793, 0.74337826936799978, 0.64395556254427311)

# # # FINDING OPTIMAL ROC OPERATING POINT

# # # Old fpr, tpr, acc
# # train_critic_OP_fpr, train_critic_OP_tpr
# # # (0.2806418572891772, 0.6403541660658149, 0.64650816445933723)
# # val_critic_OP_fpr, val_critic_OP_tpr
# # # (0.281437125748503, 0.6424870466321243, 0.64854554124940389)
# # si_critic_OP_fpr, si_critic_OP_tpr
# # # (0.31461893138052616, 0.5477734543882404, 0.6323333333333333)

# # Finding optimal point, accs
# critic_optimalOP_threshold, train_critic_optimalOP_fpr, train_critic_optimalOP_tpr, train_critic_optimalOP_acc = \
#     find_ROC_optimalOP(train_critic_fpr, train_critic_tpr, train_critic_thresholds, train_critic_preds, train_lipreader_preds_correct_or_wrong)

# val_critic_optimalOP_fpr, val_critic_optimalOP_tpr, val_critic_optimalOP_acc = find_fpr_tpr_acc_from_thresh(val_lipreader_preds_correct_or_wrong, val_critic_preds, optimalOP_threshold)
# si_critic_optimalOP_fpr, si_critic_optimalOP_tpr, si_critic_optimalOP_acc = find_fpr_tpr_acc_from_thresh(si_lipreader_preds_correct_or_wrong, si_critic_preds, optimalOP_threshold)

# # New fpr, tpr, acc
# train_critic_optimalOP_fpr, train_critic_optimalOP_tpr, train_critic_optimalOP_acc
# # (0.26971662683509728, 0.63262480892913797, 0.64023190255837459)
# val_critic_optimalOP_fpr, val_critic_optimalOP_tpr, val_critic_optimalOP_acc
# # (0.25748502994011974, 0.6259067357512953, 0.63519313304721026)
# si_critic_optimalOP_fpr, si_critic_optimalOP_tpr, si_critic_optimalOP_acc
# # (0.29210740439381611, 0.52983138780804151, 0.63924999999999998)

# np.savez('ROC_C3DCritic',
#     train_critic_score=train_critic_preds, val_critic_score=val_critic_preds, si_critic_score=si_critic_preds,
#     train_critic_fpr=train_critic_fpr, train_critic_tpr=train_critic_tpr, train_critic_thresholds=train_critic_thresholds, train_critic_roc_auc=train_critic_roc_auc,
#     val_critic_fpr=val_critic_fpr, val_critic_tpr=val_critic_tpr, val_critic_thresholds=val_critic_thresholds, val_critic_roc_auc=val_critic_roc_auc,
#     si_critic_fpr=si_critic_fpr, si_critic_tpr=si_critic_tpr, si_critic_thresholds=si_critic_thresholds, si_critic_roc_auc=si_critic_roc_auc,
#     train_critic_OP_fpr=train_critic_OP_fpr, train_critic_OP_tpr=train_critic_OP_tpr,
#     val_critic_OP_fpr=val_critic_OP_fpr, val_critic_OP_tpr=val_critic_OP_tpr,
#     si_critic_OP_fpr=si_critic_OP_fpr, si_critic_OP_tpr=si_critic_OP_tpr,
#     critic_optimalOP_threshold=critic_optimalOP_threshold,
#     train_critic_optimalOP_fpr=train_critic_optimalOP_fpr, train_critic_optimalOP_tpr=train_critic_optimalOP_tpr,
#     val_critic_optimalOP_fpr=val_critic_optimalOP_fpr, val_critic_optimalOP_tpr=val_critic_optimalOP_tpr,
#     si_critic_optimalOP_fpr=si_critic_optimalOP_fpr, si_critic_optimalOP_tpr=si_critic_optimalOP_tpr)

# Load
ROC_critic = np.load('ROC_C3DCritic.npz')
train_critic_score, val_critic_score, si_critic_score, \
        train_critic_fpr, train_critic_tpr, train_critic_thresholds, train_critic_roc_auc, \
        val_critic_fpr, val_critic_tpr, val_critic_thresholds, val_critic_roc_auc, \
        si_critic_fpr, si_critic_tpr, si_critic_thresholds, si_critic_roc_auc , \
        train_critic_OP_fpr, train_critic_OP_tpr, \
        val_critic_OP_fpr, val_critic_OP_tpr, \
        si_critic_OP_fpr, si_critic_OP_tpr, \
        critic_optimalOP_threshold, \
        train_critic_optimalOP_fpr, train_critic_optimalOP_tpr, \
        val_critic_optimalOP_fpr, val_critic_optimalOP_tpr, \
        si_critic_optimalOP_fpr, si_critic_optimalOP_tpr = \
    ROC_critic['train_critic_score'], ROC_critic['val_critic_score'], ROC_critic['si_critic_score'], \
        ROC_critic['train_critic_fpr'], ROC_critic['train_critic_tpr'], ROC_critic['train_critic_thresholds'], ROC_critic['train_critic_roc_auc'].item(), \
        ROC_critic['val_critic_fpr'], ROC_critic['val_critic_tpr'], ROC_critic['val_critic_thresholds'], ROC_critic['val_critic_roc_auc'].item(), \
        ROC_critic['si_critic_fpr'], ROC_critic['si_critic_tpr'], ROC_critic['si_critic_thresholds'], ROC_critic['si_critic_roc_auc'].item(), \
        ROC_critic['train_critic_OP_fpr'].item(), ROC_critic['train_critic_OP_tpr'].item(), \
        ROC_critic['val_critic_OP_fpr'].item(), ROC_critic['val_critic_OP_tpr'].item(), \
        ROC_critic['si_critic_OP_fpr'].item(), ROC_critic['si_critic_OP_tpr'].item(), \
        ROC_critic['critic_optimalOP_threshold'].item(), \
        ROC_critic['train_critic_optimalOP_fpr'].item(), ROC_critic['train_critic_optimalOP_tpr'].item(), \
        ROC_critic['val_critic_optimalOP_fpr'].item(), ROC_critic['val_critic_optimalOP_tpr'].item(), \
        ROC_critic['si_critic_optimalOP_fpr'].item(), ROC_critic['si_critic_optimalOP_tpr'].item()


#############################################################
# LOGISTIC REGRESSOR ROC
#############################################################

# logReg_unopt = LogisticRegression()
# logReg_unopt.fit(train_matrix, train_lipreader_preds_correct_or_wrong)

# # Save
# joblib.dump(logReg_unopt, 'logReg_unopt.pkl', compress=3)

# # Acc
# logReg_unopt.score(train_matrix, train_lipreader_preds_correct_or_wrong)
# logReg_unopt.score(val_matrix, val_lipreader_preds_correct_or_wrong)
# logReg_unopt.score(si_matrix, si_lipreader_preds_correct_or_wrong)
# # >>> # Acc
# # ... logReg_unopt.score(train_matrix, train_lipreader_preds_correct_or_wrong)
# # 0.92226477315036437
# # >>> logReg_unopt.score(val_matrix, val_lipreader_preds_correct_or_wrong)
# # 0.92083929422985222
# # >>> logReg_unopt.score(si_matrix, si_lipreader_preds_correct_or_wrong)
# # 0.38700000000000001

# # CONFUSION MATRIX, OPERATING POINT
# train_logReg_unopt_OP_fpr, train_logReg_unopt_OP_tpr, \
#         val_logReg_unopt_OP_fpr, val_logReg_unopt_OP_tpr, \
#         si_logReg_unopt_OP_fpr, si_logReg_unopt_OP_tpr = \
#     calc_grid_operating_points(logReg_unopt,
#         train_lipreader_preds_correct_or_wrong, val_lipreader_preds_correct_or_wrong, si_lipreader_preds_correct_or_wrong,
#         train_matrix, val_matrix, si_matrix)

# # Scores
# train_logReg_unopt_score = logReg_unopt.decision_function(train_matrix)
# val_logReg_unopt_score = logReg_unopt.decision_function(val_matrix)
# si_logReg_unopt_score = logReg_unopt.decision_function(si_matrix)

# # Compute ROC
# train_logReg_unopt_fpr, train_logReg_unopt_tpr, train_logReg_unopt_thresholds, train_logReg_unopt_roc_auc, \
#         val_logReg_unopt_fpr, val_logReg_unopt_tpr, val_logReg_unopt_thresholds, val_logReg_unopt_roc_auc, \
#         si_logReg_unopt_fpr, si_logReg_unopt_tpr, si_logReg_unopt_thresholds, si_logReg_unopt_roc_auc = \
#     compute_ROC_grid_singleclass(train_lipreader_preds_correct_or_wrong, train_logReg_unopt_score,
#         val_lipreader_preds_correct_or_wrong, val_logReg_unopt_score,
#         si_lipreader_preds_correct_or_wrong, si_logReg_unopt_score,
#         train_logReg_unopt_OP_fpr, train_logReg_unopt_OP_tpr,
#         val_logReg_unopt_OP_fpr, val_logReg_unopt_OP_tpr,
#         si_logReg_unopt_OP_fpr, si_logReg_unopt_OP_tpr,
#         savePlot=True, showPlot=True,
#         plot_title='ROC curve of Logistic Regressor (unoptimized)')

# train_logReg_unopt_roc_auc, val_logReg_unopt_roc_auc, si_logReg_unopt_roc_auc
# # (0.83961853740044889, 0.85645031181160991, 0.62133158287065327)

# # FINDING OPTIMAL ROC OPERATING POINT

# # Old fpr, tpr, acc
# train_logReg_unopt_OP_fpr, train_logReg_unopt_OP_tpr
# # (0.98463639467395014, 0.99887520549130449, 0.92226477315036437)
# val_logReg_unopt_OP_fpr, val_logReg_unopt_OP_tpr
# # (0.9880239520958084, 0.99948186528497407, 0.92083929422985222)
# si_logReg_unopt_OP_fpr, si_logReg_unopt_OP_tpr
# # (0.9972877678329265, 0.99956766104626027, 0.38700000000000001)

# # Finding optimal point, accs
# logReg_unopt_optimalOP_threshold, train_logReg_unopt_optimalOP_fpr, train_logReg_unopt_optimalOP_tpr, train_logReg_unopt_optimalOP_acc = \
#     find_ROC_optimalOP(train_logReg_unopt_fpr, train_logReg_unopt_tpr, train_logReg_unopt_thresholds, train_logReg_unopt_score, train_lipreader_preds_correct_or_wrong)

# val_logReg_unopt_optimalOP_fpr, val_logReg_unopt_optimalOP_tpr, val_logReg_unopt_optimalOP_acc = find_fpr_tpr_acc_from_thresh(val_lipreader_preds_correct_or_wrong, val_logReg_unopt_score, optimalOP_threshold)
# si_logReg_unopt_optimalOP_fpr, si_logReg_unopt_optimalOP_tpr, si_logReg_unopt_optimalOP_acc = find_fpr_tpr_acc_from_thresh(si_lipreader_preds_correct_or_wrong, si_logReg_unopt_score, optimalOP_threshold)

# # New fpr, tpr, acc
# train_logReg_unopt_optimalOP_fpr, train_logReg_unopt_optimalOP_tpr, train_logReg_unopt_optimalOP_acc
# # (0.20382383065892795, 0.73812476566781071, 0.74264666773043986)
# val_logReg_unopt_optimalOP_fpr, val_logReg_unopt_optimalOP_tpr, val_logReg_unopt_optimalOP_acc
# # (0.24251497005988024, 0.79119170984455955, 0.78850739151168336)
# si_logReg_unopt_optimalOP_fpr, si_logReg_unopt_optimalOP_tpr, si_logReg_unopt_optimalOP_acc
# # (0.59262272850556008, 0.79442282749675741, 0.55658333333333332)

# plot_grid_ROC(train_logReg_unopt_fpr, train_logReg_unopt_tpr, train_logReg_unopt_roc_auc,
#         val_logReg_unopt_fpr, val_logReg_unopt_tpr, val_logReg_unopt_roc_auc,
#         si_logReg_unopt_fpr, si_logReg_unopt_tpr, si_logReg_unopt_roc_auc,
#         train_OP_fpr=train_logReg_unopt_OP_fpr, train_OP_tpr=train_logReg_unopt_OP_tpr,
#         val_OP_fpr=val_logReg_unopt_OP_fpr, val_OP_tpr=val_logReg_unopt_OP_tpr,
#         si_OP_fpr=si_logReg_unopt_OP_fpr, si_OP_tpr=si_logReg_unopt_OP_tpr,
#         train_optimalOP_fpr=train_logReg_unopt_optimalOP_fpr, train_optimalOP_tpr=train_logReg_unopt_optimalOP_tpr,
#         val_optimalOP_fpr=val_logReg_unopt_optimalOP_fpr, val_optimalOP_tpr=val_logReg_unopt_optimalOP_tpr,
#         si_optimalOP_fpr=si_logReg_unopt_optimalOP_fpr, si_optimalOP_tpr=si_logReg_unopt_optimalOP_tpr,
#         plot_title='ROC curve of Logistic Regressor (unoptimized)')

# np.savez('ROC_logReg_unopt',
#     train_logReg_unopt_score=train_logReg_unopt_score, val_logReg_unopt_score=val_logReg_unopt_score, si_logReg_unopt_score=si_logReg_unopt_score,
#     train_logReg_unopt_fpr=train_logReg_unopt_fpr, train_logReg_unopt_tpr=train_logReg_unopt_tpr, train_logReg_unopt_thresholds=train_logReg_unopt_thresholds, train_logReg_unopt_roc_auc=train_logReg_unopt_roc_auc,
#     val_logReg_unopt_fpr=val_logReg_unopt_fpr, val_logReg_unopt_tpr=val_logReg_unopt_tpr, val_logReg_unopt_thresholds=val_logReg_unopt_thresholds, val_logReg_unopt_roc_auc=val_logReg_unopt_roc_auc,
#     si_logReg_unopt_fpr=si_logReg_unopt_fpr, si_logReg_unopt_tpr=si_logReg_unopt_tpr, si_logReg_unopt_thresholds=si_logReg_unopt_thresholds, si_logReg_unopt_roc_auc=si_logReg_unopt_roc_auc,
#     train_logReg_unopt_OP_fpr=train_logReg_unopt_OP_fpr, train_logReg_unopt_OP_tpr=train_logReg_unopt_OP_tpr,
#     val_logReg_unopt_OP_fpr=val_logReg_unopt_OP_fpr, val_logReg_unopt_OP_tpr=val_logReg_unopt_OP_tpr,
#     si_logReg_unopt_OP_fpr=si_logReg_unopt_OP_fpr, si_logReg_unopt_OP_tpr=si_logReg_unopt_OP_tpr,
#     logReg_unopt_optimalOP_threshold=logReg_unopt_optimalOP_threshold,
#     train_logReg_unopt_optimalOP_fpr=train_logReg_unopt_optimalOP_fpr, train_logReg_unopt_optimalOP_tpr=train_logReg_unopt_optimalOP_tpr,
#     val_logReg_unopt_optimalOP_fpr=val_logReg_unopt_optimalOP_fpr, val_logReg_unopt_optimalOP_tpr=val_logReg_unopt_optimalOP_tpr,
#     si_logReg_unopt_optimalOP_fpr=si_logReg_unopt_optimalOP_fpr, si_logReg_unopt_optimalOP_tpr=si_logReg_unopt_optimalOP_tpr)

# Load
logReg_unopt = joblib.load('logReg_unopt.pkl')
ROC_logReg_unopt = np.load('ROC_logReg_unopt.npz')
train_logReg_unopt_score, val_logReg_unopt_score, si_logReg_unopt_score, \
        train_logReg_unopt_fpr, train_logReg_unopt_tpr, train_logReg_unopt_thresholds, train_logReg_unopt_roc_auc, \
        val_logReg_unopt_fpr, val_logReg_unopt_tpr, val_logReg_unopt_thresholds, val_logReg_unopt_roc_auc, \
        si_logReg_unopt_fpr, si_logReg_unopt_tpr, si_logReg_unopt_thresholds, si_logReg_unopt_roc_auc , \
        train_logReg_unopt_OP_fpr, train_logReg_unopt_OP_tpr, \
        val_logReg_unopt_OP_fpr, val_logReg_unopt_OP_tpr, \
        si_logReg_unopt_OP_fpr, si_logReg_unopt_OP_tpr, \
        train_logReg_unopt_optimalOP_fpr, train_logReg_unopt_optimalOP_tpr, \
        val_logReg_unopt_optimalOP_fpr, val_logReg_unopt_optimalOP_tpr, \
        si_logReg_unopt_optimalOP_fpr, si_logReg_unopt_optimalOP_tpr = \
    ROC_logReg_unopt['train_logReg_unopt_score'], ROC_logReg_unopt['val_logReg_unopt_score'], ROC_logReg_unopt['si_logReg_unopt_score'], \
        ROC_logReg_unopt['train_logReg_unopt_fpr'], ROC_logReg_unopt['train_logReg_unopt_tpr'], ROC_logReg_unopt['train_logReg_unopt_thresholds'], ROC_logReg_unopt['train_logReg_unopt_roc_auc'].item(), \
        ROC_logReg_unopt['val_logReg_unopt_fpr'], ROC_logReg_unopt['val_logReg_unopt_tpr'], ROC_logReg_unopt['val_logReg_unopt_thresholds'], ROC_logReg_unopt['val_logReg_unopt_roc_auc'].item(), \
        ROC_logReg_unopt['si_logReg_unopt_fpr'], ROC_logReg_unopt['si_logReg_unopt_tpr'], ROC_logReg_unopt['si_logReg_unopt_thresholds'], ROC_logReg_unopt['si_logReg_unopt_roc_auc'].item(), \
        ROC_logReg_unopt['train_logReg_unopt_OP_fpr'].item(), ROC_logReg_unopt['train_logReg_unopt_OP_tpr'].item(), \
        ROC_logReg_unopt['val_logReg_unopt_OP_fpr'].item(), ROC_logReg_unopt['val_logReg_unopt_OP_tpr'].item(), \
        ROC_logReg_unopt['si_logReg_unopt_OP_fpr'].item(), ROC_logReg_unopt['si_logReg_unopt_OP_tpr'].item(), \
        ROC_logReg_unopt['train_logReg_unopt_optimalOP_fpr'].item(), ROC_logReg_unopt['train_logReg_unopt_optimalOP_tpr'].item(), \
        ROC_logReg_unopt['val_logReg_unopt_optimalOP_fpr'].item(), ROC_logReg_unopt['val_logReg_unopt_optimalOP_tpr'].item(), \
        ROC_logReg_unopt['si_logReg_unopt_optimalOP_fpr'].item(), ROC_logReg_unopt['si_logReg_unopt_optimalOP_tpr'].item()


#############################################################
# SVM ROC
#############################################################

#####################################
# LINEAR UNOPT
#####################################

# SVM_linear_unopt = SVC(kernel='linear', class_weight='balanced', probability=True)
# SVM_linear_unopt.fit(train_matrix, train_lipreader_preds_correct_or_wrong)

# # Save
# joblib.dump(SVM_linear_unopt, 'default_SVM_linear.pkl', compress=3)

# # Acc
# SVM_linear_unopt.score(train_matrix, train_lipreader_preds_correct_or_wrong)
# SVM_linear_unopt.score(val_matrix, val_lipreader_preds_correct_or_wrong)
# SVM_linear_unopt.score(si_matrix, si_lipreader_preds_correct_or_wrong)

# # CONFUSION MATRIX, OPERATING POINT
# train_logReg_unopt_OP_fpr, train_logReg_unopt_OP_tpr, \
#         val_logReg_unopt_OP_fpr, val_logReg_unopt_OP_tpr, \
#         si_logReg_unopt_OP_fpr, si_logReg_unopt_OP_tpr = \
#     calc_grid_operating_points(SVM_linear_unopt,
#         train_lipreader_preds_correct_or_wrong, val_lipreader_preds_correct_or_wrong, si_lipreader_preds_correct_or_wrong,
#         train_matrix, val_matrix, si_matrix)

# # Scores
# train_SVM_linear_unopt_score = SVM_linear_unopt.decision_function(train_matrix)
# val_SVM_linear_unopt_score = SVM_linear_unopt.decision_function(val_matrix)
# si_SVM_linear_unopt_score = SVM_linear_unopt.decision_function(si_matrix)

# # Compute ROC
# train_SVM_linear_unopt_fpr, train_SVM_linear_unopt_tpr, train_SVM_linear_unopt_thresholds, train_SVM_linear_unopt_roc_auc, \
#         val_SVM_linear_unopt_fpr, val_SVM_linear_unopt_tpr, val_SVM_linear_unopt_thresholds, val_SVM_linear_unopt_roc_auc, \
#         si_SVM_linear_unopt_fpr, si_SVM_linear_unopt_tpr, si_SVM_linear_unopt_thresholds, si_SVM_linear_unopt_roc_auc = \
#     compute_ROC_grid_singleclass(train_lipreader_preds_correct_or_wrong, train_SVM_linear_unopt_score,
#         val_lipreader_preds_correct_or_wrong, val_SVM_linear_unopt_score,
#         si_lipreader_preds_correct_or_wrong, si_SVM_linear_unopt_score,
#         train_logReg_unopt_OP_fpr, train_logReg_unopt_OP_tpr,
#         val_logReg_unopt_OP_fpr, val_logReg_unopt_OP_tpr,
#         si_logReg_unopt_OP_fpr, si_logReg_unopt_OP_tpr,
#         savePlot=True, showPlot=True,
#         plot_title='ROC curve of linear SVM (unoptimized)')

# train_SVM_linear_unopt_roc_auc, val_SVM_linear_unopt_roc_auc, si_SVM_linear_unopt_roc_auc
# # (0.83961853740044

# np.savez('ROC_linearSVM_unopt',
#     train_SVM_linear_unopt_score=train_SVM_linear_unopt_score, val_SVM_linear_unopt_score=val_SVM_linear_unopt_score, si_SVM_linear_unopt_score=si_SVM_linear_unopt_score,
#     train_SVM_linear_unopt_fpr=train_SVM_linear_unopt_fpr, train_SVM_linear_unopt_tpr=train_SVM_linear_unopt_tpr, train_SVM_linear_unopt_roc_auc=train_SVM_linear_unopt_roc_auc,
#     val_SVM_linear_unopt_fpr=val_SVM_linear_unopt_fpr, val_SVM_linear_unopt_tpr=val_SVM_linear_unopt_tpr, val_SVM_linear_unopt_roc_auc=val_SVM_linear_unopt_roc_auc,
#     si_SVM_linear_unopt_fpr=si_SVM_linear_unopt_fpr, si_SVM_linear_unopt_tpr=si_SVM_linear_unopt_tpr, si_SVM_linear_unopt_roc_auc=si_SVM_linear_unopt_roc_auc)

# # Load
# SVM_linear_unopt = joblib.load('default_SVM_linear.pkl') 


#####################################
# LINEAR OPT
#####################################

# # score function: twice iterated 10-fold cross-validated accuracy
# @optunity.cross_validated(x=train_matrix, y=train_lipreader_preds_correct_or_wrong, num_folds=2, num_iter=1)
# def svm_linear_auc(x_train, y_train, x_test, y_test, logC, logGamma):
#     model = SVC(kernel='linear', C=10 ** logC, gamma=10 ** logGamma, class_weight='balanced').fit(x_train, y_train)
#     decision_values = model.decision_function(x_test)
#     return optunity.metrics.roc_auc(y_test, decision_values)

# # perform tuning on linear
# hps_linear, _, _ = optunity.maximize(svm_linear_auc, num_evals=10, logC=[-5, 2], logGamma=[-5, 1])
# hps_linear = {'logC': 1.14892578125, 'logGamma': -4.9794921875} # features 3:11
# hps_linear = {'logC': -1.07275390625, 'logGamma': -0.8486328125} # features 3:71

# # train model on the full training set with tuned hyperparameters
# SVM_linear_optimal = SVC(kernel='linear', C=10 ** hps_linear['logC'], gamma=10 ** hps_linear['logGamma'], class_weight='balanced', probability=True).fit(train_matrix, train_lipreader_preds_correct_or_wrong)

# # Save
# joblib.dump(SVM_linear_optimal, 'SVM_linear_optimal.pkl', compress=3) 

# # Acc
# SVM_linear_optimal.score(train_matrix, train_lipreader_preds_correct_or_wrong)
# SVM_linear_optimal.score(val_matrix, val_lipreader_preds_correct_or_wrong)
# SVM_linear_optimal.score(si_matrix, si_lipreader_preds_correct_or_wrong)
# # >>> # Acc
# # ... SVM_linear_optimal.score(train_matrix, train_lipreader_preds_correct_or_wrong)
# # 0.73557257592681236
# # >>> SVM_linear_optimal.score(val_matrix, val_lipreader_preds_correct_or_wrong)
# # 0.78969957081545061
# # >>> SVM_linear_optimal.score(si_matrix, si_lipreader_preds_correct_or_wrong)
# # 0.54808333333333337

# # CONFUSION MATRIX, OPERATING POINT
# train_SVM_linear_opt_OP_fpr, train_SVM_linear_opt_OP_tpr, \
#         val_SVM_linear_opt_OP_fpr, val_SVM_linear_opt_OP_tpr, \
#         si_SVM_linear_opt_OP_fpr, si_SVM_linear_opt_OP_tpr = \
#     calc_grid_operating_points(SVM_linear_optimal,
#         train_lipreader_preds_correct_or_wrong, val_lipreader_preds_correct_or_wrong, si_lipreader_preds_correct_or_wrong,
#         train_matrix, val_matrix, si_matrix)

# # Scores
# train_SVM_linear_opt_score = SVM_linear_optimal.decision_function(train_matrix)
# val_SVM_linear_opt_score = SVM_linear_optimal.decision_function(val_matrix)
# si_SVM_linear_opt_score = SVM_linear_optimal.decision_function(si_matrix)

# # Compute ROC
# train_SVM_linear_opt_fpr, train_SVM_linear_opt_tpr, train_SVM_linear_opt_thresholds, train_SVM_linear_opt_roc_auc, \
#         val_SVM_linear_opt_fpr, val_SVM_linear_opt_tpr, val_SVM_linear_opt_thresholds, val_SVM_linear_opt_roc_auc, \
#         si_SVM_linear_opt_fpr, si_SVM_linear_opt_tpr, si_SVM_linear_opt_thresholds, si_SVM_linear_opt_roc_auc = \
#     compute_ROC_grid_singleclass(train_lipreader_preds_correct_or_wrong, train_SVM_linear_opt_score,
#         val_lipreader_preds_correct_or_wrong, val_SVM_linear_opt_score,
#         si_lipreader_preds_correct_or_wrong, si_SVM_linear_opt_score,
#         train_SVM_linear_opt_OP_fpr, train_SVM_linear_opt_OP_tpr,
#         val_SVM_linear_opt_OP_fpr, val_SVM_linear_opt_OP_tpr,
#         si_SVM_linear_opt_OP_fpr, si_SVM_linear_opt_OP_tpr,
#         savePlot=True, showPlot=True,
#         plot_title='ROC curve of linear SVM (optimized)')

# # FINDING OPTIMAL ROC OPERATING POINT

# # Old fpr, tpr, acc
# train_SVM_linear_opt_OP_fpr, train_SVM_linear_opt_OP_tpr
# # (0.19528849436667806, 0.7297320681798518, 0.73557257592681236)
# val_SVM_linear_opt_OP_fpr, val_SVM_linear_opt_OP_tpr
# # (0.23053892215568864, 0.7914507772020726, 0.78969957081545061)
# si_SVM_linear_opt_OP_fpr, si_SVM_linear_opt_OP_tpr
# # (0.6181177108760509, 0.8130134025075659, 0.54808333333333337)

# # Finding optimal point, accs
# SVM_linear_opt_optimalOP_threshold, train_SVM_linear_opt_optimalOP_fpr, train_SVM_linear_opt_optimalOP_tpr, train_SVM_linear_opt_optimalOP_acc = \
#     find_ROC_optimalOP(train_SVM_linear_opt_fpr, train_SVM_linear_opt_tpr, train_SVM_linear_opt_thresholds, train_SVM_linear_opt_score, train_lipreader_preds_correct_or_wrong)

# val_SVM_linear_opt_optimalOP_fpr, val_SVM_linear_opt_optimalOP_tpr, val_SVM_linear_opt_optimalOP_acc = find_fpr_tpr_acc_from_thresh(val_lipreader_preds_correct_or_wrong, val_SVM_linear_opt_score, optimalOP_threshold)
# si_SVM_linear_opt_optimalOP_fpr, si_SVM_linear_opt_optimalOP_tpr, si_SVM_linear_opt_optimalOP_acc = find_fpr_tpr_acc_from_thresh(si_lipreader_preds_correct_or_wrong, si_SVM_linear_opt_score, optimalOP_threshold)

# # New fpr, tpr, acc
# train_SVM_linear_opt_optimalOP_fpr, train_SVM_linear_opt_optimalOP_tpr, train_SVM_linear_opt_optimalOP_acc
# # (0.21338340730624786, 0.74937271075476597, 0.75227381522259451)
# val_SVM_linear_opt_optimalOP_fpr, val_SVM_linear_opt_optimalOP_tpr, val_SVM_linear_opt_optimalOP_acc
# # (0.25449101796407186, 0.80569948186528495, 0.80090605627086309)
# si_SVM_linear_opt_optimalOP_fpr, si_SVM_linear_opt_optimalOP_tpr, si_SVM_linear_opt_optimalOP_acc
# # (0.64144290751288313, 0.83073929961089499, 0.5405833333333333)

# plot_grid_ROC(train_SVM_linear_opt_fpr, train_SVM_linear_opt_tpr, train_SVM_linear_opt_roc_auc,
#         val_SVM_linear_opt_fpr, val_SVM_linear_opt_tpr, val_SVM_linear_opt_roc_auc,
#         si_SVM_linear_opt_fpr, si_SVM_linear_opt_tpr, si_SVM_linear_opt_roc_auc,
#         train_OP_fpr=train_SVM_linear_opt_OP_fpr, train_OP_tpr=train_SVM_linear_opt_OP_tpr,
#         val_OP_fpr=val_SVM_linear_opt_OP_fpr, val_OP_tpr=val_SVM_linear_opt_OP_tpr,
#         si_OP_fpr=si_SVM_linear_opt_OP_fpr, si_OP_tpr=si_SVM_linear_opt_OP_tpr,
#         train_optimalOP_fpr=train_SVM_linear_opt_optimalOP_fpr, train_optimalOP_tpr=train_SVM_linear_opt_optimalOP_tpr,
#         val_optimalOP_fpr=val_SVM_linear_opt_optimalOP_fpr, val_optimalOP_tpr=val_SVM_linear_opt_optimalOP_tpr,
#         si_optimalOP_fpr=si_SVM_linear_opt_optimalOP_fpr, si_optimalOP_tpr=si_SVM_linear_opt_optimalOP_tpr,
#         plot_title='ROC curve of linear SVM (optimized)')

# np.savez('ROC_SVM_linear_opt',
#     train_SVM_linear_opt_score=train_SVM_linear_opt_score, val_SVM_linear_opt_score=val_SVM_linear_opt_score, si_SVM_linear_opt_score=si_SVM_linear_opt_score,
#     train_SVM_linear_opt_fpr=train_SVM_linear_opt_fpr, train_SVM_linear_opt_tpr=train_SVM_linear_opt_tpr, train_SVM_linear_opt_thresholds=train_SVM_linear_opt_thresholds, train_SVM_linear_opt_roc_auc=train_SVM_linear_opt_roc_auc,
#     val_SVM_linear_opt_fpr=val_SVM_linear_opt_fpr, val_SVM_linear_opt_tpr=val_SVM_linear_opt_tpr, val_SVM_linear_opt_thresholds=val_SVM_linear_opt_thresholds, val_SVM_linear_opt_roc_auc=val_SVM_linear_opt_roc_auc,
#     si_SVM_linear_opt_fpr=si_SVM_linear_opt_fpr, si_SVM_linear_opt_tpr=si_SVM_linear_opt_tpr, si_SVM_linear_opt_thresholds=si_SVM_linear_opt_thresholds, si_SVM_linear_opt_roc_auc=si_SVM_linear_opt_roc_auc,
#     train_SVM_linear_opt_OP_fpr=train_SVM_linear_opt_OP_fpr, train_SVM_linear_opt_OP_tpr=train_SVM_linear_opt_OP_tpr,
#     val_SVM_linear_opt_OP_fpr=val_SVM_linear_opt_OP_fpr, val_SVM_linear_opt_OP_tpr=val_SVM_linear_opt_OP_tpr,
#     si_SVM_linear_opt_OP_fpr=si_SVM_linear_opt_OP_fpr, si_SVM_linear_opt_OP_tpr=si_SVM_linear_opt_OP_tpr,
#     SVM_linear_opt_optimalOP_threshold=SVM_linear_opt_optimalOP_threshold,
#     train_SVM_linear_opt_optimalOP_fpr=train_SVM_linear_opt_optimalOP_fpr, train_SVM_linear_opt_optimalOP_tpr=train_SVM_linear_opt_optimalOP_tpr,
#     val_SVM_linear_opt_optimalOP_fpr=val_SVM_linear_opt_optimalOP_fpr, val_SVM_linear_opt_optimalOP_tpr=val_SVM_linear_opt_optimalOP_tpr,
#     si_SVM_linear_opt_optimalOP_fpr=si_SVM_linear_opt_optimalOP_fpr, si_SVM_linear_opt_optimalOP_tpr=si_SVM_linear_opt_optimalOP_tpr)

# Load
SVM_linear_optimal = joblib.load('SVM_linear_optimal.pkl')
ROC_SVM_linear_opt = np.load('ROC_SVM_linear_opt.npz')
train_SVM_linear_opt_score, val_SVM_linear_opt_score, si_SVM_linear_opt_score, \
        train_SVM_linear_opt_fpr, train_SVM_linear_opt_tpr, train_SVM_linear_opt_thresholds, train_SVM_linear_opt_roc_auc, \
        val_SVM_linear_opt_fpr, val_SVM_linear_opt_tpr, val_SVM_linear_opt_thresholds, val_SVM_linear_opt_roc_auc, \
        si_SVM_linear_opt_fpr, si_SVM_linear_opt_tpr, si_SVM_linear_opt_thresholds, si_SVM_linear_opt_roc_auc , \
        train_SVM_linear_opt_OP_fpr, train_SVM_linear_opt_OP_tpr, \
        val_SVM_linear_opt_OP_fpr, val_SVM_linear_opt_OP_tpr, \
        si_SVM_linear_opt_OP_fpr, si_SVM_linear_opt_OP_tpr, \
        train_SVM_linear_opt_optimalOP_fpr, train_SVM_linear_opt_optimalOP_tpr, \
        val_SVM_linear_opt_optimalOP_fpr, val_SVM_linear_opt_optimalOP_tpr, \
        si_SVM_linear_opt_optimalOP_fpr, si_SVM_linear_opt_optimalOP_tpr = \
    ROC_SVM_linear_opt['train_SVM_linear_opt_score'], ROC_SVM_linear_opt['val_SVM_linear_opt_score'], ROC_SVM_linear_opt['si_SVM_linear_opt_score'], \
        ROC_SVM_linear_opt['train_SVM_linear_opt_fpr'], ROC_SVM_linear_opt['train_SVM_linear_opt_tpr'], ROC_SVM_linear_opt['train_SVM_linear_opt_thresholds'], ROC_SVM_linear_opt['train_SVM_linear_opt_roc_auc'].item(), \
        ROC_SVM_linear_opt['val_SVM_linear_opt_fpr'], ROC_SVM_linear_opt['val_SVM_linear_opt_tpr'], ROC_SVM_linear_opt['val_SVM_linear_opt_thresholds'], ROC_SVM_linear_opt['val_SVM_linear_opt_roc_auc'].item(), \
        ROC_SVM_linear_opt['si_SVM_linear_opt_fpr'], ROC_SVM_linear_opt['si_SVM_linear_opt_tpr'], ROC_SVM_linear_opt['si_SVM_linear_opt_thresholds'], ROC_SVM_linear_opt['si_SVM_linear_opt_roc_auc'].item(), \
        ROC_SVM_linear_opt['train_SVM_linear_opt_OP_fpr'].item(), ROC_SVM_linear_opt['train_SVM_linear_opt_OP_tpr'].item(), \
        ROC_SVM_linear_opt['val_SVM_linear_opt_OP_fpr'].item(), ROC_SVM_linear_opt['val_SVM_linear_opt_OP_tpr'].item(), \
        ROC_SVM_linear_opt['si_SVM_linear_opt_OP_fpr'].item(), ROC_SVM_linear_opt['si_SVM_linear_opt_OP_tpr'].item(), \
        ROC_SVM_linear_opt['train_SVM_linear_opt_optimalOP_fpr'].item(), ROC_SVM_linear_opt['train_SVM_linear_opt_optimalOP_tpr'].item(), \
        ROC_SVM_linear_opt['val_SVM_linear_opt_optimalOP_fpr'].item(), ROC_SVM_linear_opt['val_SVM_linear_opt_optimalOP_tpr'].item(), \
        ROC_SVM_linear_opt['si_SVM_linear_opt_optimalOP_fpr'].item(), ROC_SVM_linear_opt['si_SVM_linear_opt_optimalOP_tpr'].item()


#####################################
# RBF OPT
#####################################

# @optunity.cross_validated(x=train_matrix, y=train_lipreader_preds_correct_or_wrong, num_folds=2, num_iter=1)
# def svm_rbf_auc(x_train, y_train, x_test, y_test, logC, logGamma):
#     model = SVC(kernel='rbf', C=10 ** logC, gamma=10 ** logGamma, class_weight='balanced').fit(x_train, y_train)
#     decision_values = model.decision_function(x_test)
#     return optunity.metrics.roc_auc(y_test, decision_values)

# # perform tuning on rbf
# hps_rbf, _, _ = optunity.maximize(svm_rbf_auc, num_evals=10, logC=[-5, 2], logGamma=[-5, 1])
# hps_rbf = {'logC': 0.62255859375, 'logGamma': 0.1357421875} # features 3:11
# hps_rbf = {'logC': -1.63330078125, 'logGamma': 0.5693359375} # features 3:71

# # train model on the full training set with tuned hyperparameters
# SVM_rbf_optimal = SVC(kernel='rbf', C=10 ** hps_rbf['logC'], gamma=10 ** hps_rbf['logGamma'], class_weight='balanced', probability=True).fit(train_matrix, train_lipreader_preds_correct_or_wrong)

# # Save
# joblib.dump(SVM_rbf_optimal, 'SVM_rbf_optimal.pkl', compress=3) 

# # Acc
# SVM_rbf_optimal.score(train_matrix, train_lipreader_preds_correct_or_wrong)
# SVM_rbf_optimal.score(val_matrix, val_lipreader_preds_correct_or_wrong)
# SVM_rbf_optimal.score(si_matrix, si_lipreader_preds_correct_or_wrong)
# # >>> # Acc
# # ... SVM_rbf_optimal.score(train_matrix, train_lipreader_preds_correct_or_wrong)
# # 0.89825009308015535
# # >>> SVM_rbf_optimal.score(val_matrix, val_lipreader_preds_correct_or_wrong)
# # 0.90247973295183592
# # >>> SVM_rbf_optimal.score(si_matrix, si_lipreader_preds_correct_or_wrong)
# # 0.39008333333333334

# # CONFUSION MATRIX, OPERATING POINT
# train_SVM_rbf_opt_OP_fpr, train_SVM_rbf_opt_OP_tpr, \
#         val_SVM_rbf_opt_OP_fpr, val_SVM_rbf_opt_OP_tpr, \
#         si_SVM_rbf_opt_OP_fpr, si_SVM_rbf_opt_OP_tpr = \
#     calc_grid_operating_points(SVM_rbf_optimal,
#         train_lipreader_preds_correct_or_wrong, val_lipreader_preds_correct_or_wrong, si_lipreader_preds_correct_or_wrong,
#         train_matrix, val_matrix, si_matrix)

# # Scores
# train_SVM_rbf_opt_score = SVM_rbf_optimal.decision_function(train_matrix)
# val_SVM_rbf_opt_score = SVM_rbf_optimal.decision_function(val_matrix)
# si_SVM_rbf_opt_score = SVM_rbf_optimal.decision_function(si_matrix)

# # Compute ROC
# train_SVM_rbf_opt_fpr, train_SVM_rbf_opt_tpr, train_SVM_rbf_opt_thresholds, train_SVM_rbf_opt_roc_auc, \
#         val_SVM_rbf_opt_fpr, val_SVM_rbf_opt_tpr, val_SVM_rbf_opt_thresholds, val_SVM_rbf_opt_roc_auc, \
#         si_SVM_rbf_opt_fpr, si_SVM_rbf_opt_tpr, si_SVM_rbf_opt_thresholds, si_SVM_rbf_opt_roc_auc = \
#     compute_ROC_grid_singleclass(train_lipreader_preds_correct_or_wrong, train_SVM_rbf_opt_score,
#         val_lipreader_preds_correct_or_wrong, val_SVM_rbf_opt_score,
#         si_lipreader_preds_correct_or_wrong, si_SVM_rbf_opt_score,
#         train_SVM_rbf_opt_OP_fpr, train_SVM_rbf_opt_OP_tpr,
#         val_SVM_rbf_opt_OP_fpr, val_SVM_rbf_opt_OP_tpr,
#         si_SVM_rbf_opt_OP_fpr, si_SVM_rbf_opt_OP_tpr,
#         savePlot=False, showPlot=False,
#         plot_title='ROC curve of RBF SVM optimized')

# plot_grid_ROC(train_SVM_rbf_opt_fpr, train_SVM_rbf_opt_tpr, train_SVM_rbf_opt_roc_auc,
#         val_SVM_rbf_opt_fpr, val_SVM_rbf_opt_tpr, val_SVM_rbf_opt_roc_auc,
#         si_SVM_rbf_opt_fpr, si_SVM_rbf_opt_tpr, si_SVM_rbf_opt_roc_auc,
#         train_OP_fpr=train_SVM_rbf_opt_OP_fpr, train_OP_tpr=train_SVM_rbf_opt_OP_tpr,
#         val_OP_fpr=val_SVM_rbf_opt_OP_fpr, val_OP_tpr=val_SVM_rbf_opt_OP_tpr,
#         si_OP_fpr=si_SVM_rbf_opt_OP_fpr, si_OP_tpr=si_SVM_rbf_opt_OP_tpr,
#         plot_title='ROC curve of RBF SVM (optimized)')

# # FINDING OPTIMAL ROC OPERATING POINT

# # Old fpr, tpr, acc
# train_SVM_rbf_opt_OP_fpr, train_SVM_rbf_opt_OP_tpr
# # (0.5377261864117446, 0.9350791682288813, 0.89825009308015535)
# val_SVM_rbf_opt_OP_fpr, val_SVM_rbf_opt_OP_tpr
# # (0.7125748502994012, 0.955699481865285, 0.90247973295183592)
# si_SVM_rbf_opt_OP_fpr, si_SVM_rbf_opt_OP_tpr
# # (0.9911852454570111, 0.9978383052313013, 0.39008333333333334)

# # Finding optimal point, accs
# SVM_rbf_opt_optimalOP_threshold, train_SVM_rbf_opt_optimalOP_fpr, train_SVM_rbf_opt_optimalOP_tpr, train_SVM_rbf_opt_optimalOP_acc = \
#     find_ROC_optimalOP(train_SVM_rbf_opt_fpr, train_SVM_rbf_opt_tpr, train_SVM_rbf_opt_thresholds, train_SVM_rbf_opt_score, train_lipreader_preds_correct_or_wrong)

# val_SVM_rbf_opt_optimalOP_fpr, val_SVM_rbf_opt_optimalOP_tpr, val_SVM_rbf_opt_optimalOP_acc = find_fpr_tpr_acc_from_thresh(val_lipreader_preds_correct_or_wrong, val_SVM_rbf_opt_score, optimalOP_threshold)
# si_SVM_rbf_opt_optimalOP_fpr, si_SVM_rbf_opt_optimalOP_tpr, si_SVM_rbf_opt_optimalOP_acc = find_fpr_tpr_acc_from_thresh(si_lipreader_preds_correct_or_wrong, si_SVM_rbf_opt_score, optimalOP_threshold)

# # New fpr, tpr, acc
# train_SVM_rbf_opt_optimalOP_fpr, train_SVM_rbf_opt_optimalOP_tpr, train_SVM_rbf_opt_optimalOP_acc
# # (0.088084670536019122, 0.81824474374873823, 0.82554119461730757)
# val_SVM_rbf_opt_optimalOP_fpr, val_SVM_rbf_opt_optimalOP_tpr, val_SVM_rbf_opt_optimalOP_acc
# # (0.31437125748502992, 0.84430051813471507, 0.83166428230805911)
# si_SVM_rbf_opt_optimalOP_fpr, si_SVM_rbf_opt_optimalOP_tpr, si_SVM_rbf_opt_optimalOP_acc
# # (0.84187686465961487, 0.93990488543017725, 0.45950000000000002)

# plot_grid_ROC(train_SVM_rbf_opt_fpr, train_SVM_rbf_opt_tpr, train_SVM_rbf_opt_roc_auc,
#         val_SVM_rbf_opt_fpr, val_SVM_rbf_opt_tpr, val_SVM_rbf_opt_roc_auc,
#         si_SVM_rbf_opt_fpr, si_SVM_rbf_opt_tpr, si_SVM_rbf_opt_roc_auc,
#         train_OP_fpr=train_SVM_rbf_opt_OP_fpr, train_OP_tpr=train_SVM_rbf_opt_OP_tpr,
#         val_OP_fpr=val_SVM_rbf_opt_OP_fpr, val_OP_tpr=val_SVM_rbf_opt_OP_tpr,
#         si_OP_fpr=si_SVM_rbf_opt_OP_fpr, si_OP_tpr=si_SVM_rbf_opt_OP_tpr,
#         train_optimalOP_fpr=train_SVM_rbf_opt_optimalOP_fpr, train_optimalOP_tpr=train_SVM_rbf_opt_optimalOP_tpr,
#         val_optimalOP_fpr=val_SVM_rbf_opt_optimalOP_fpr, val_optimalOP_tpr=val_SVM_rbf_opt_optimalOP_tpr,
#         si_optimalOP_fpr=si_SVM_rbf_opt_optimalOP_fpr, si_optimalOP_tpr=si_SVM_rbf_opt_optimalOP_tpr,
#         plot_title='ROC curve of RBF SVM (optimized)')

# np.savez('ROC_SVM_rbf_opt',
#     train_SVM_rbf_opt_score=train_SVM_rbf_opt_score, val_SVM_rbf_opt_score=val_SVM_rbf_opt_score, si_SVM_rbf_opt_score=si_SVM_rbf_opt_score,
#     train_SVM_rbf_opt_fpr=train_SVM_rbf_opt_fpr, train_SVM_rbf_opt_tpr=train_SVM_rbf_opt_tpr, train_SVM_rbf_opt_thresholds=train_SVM_rbf_opt_thresholds, train_SVM_rbf_opt_roc_auc=train_SVM_rbf_opt_roc_auc,
#     val_SVM_rbf_opt_fpr=val_SVM_rbf_opt_fpr, val_SVM_rbf_opt_tpr=val_SVM_rbf_opt_tpr, val_SVM_rbf_opt_thresholds=val_SVM_rbf_opt_thresholds, val_SVM_rbf_opt_roc_auc=val_SVM_rbf_opt_roc_auc,
#     si_SVM_rbf_opt_fpr=si_SVM_rbf_opt_fpr, si_SVM_rbf_opt_tpr=si_SVM_rbf_opt_tpr, si_SVM_rbf_opt_thresholds=si_SVM_rbf_opt_thresholds, si_SVM_rbf_opt_roc_auc=si_SVM_rbf_opt_roc_auc,
#     train_SVM_rbf_opt_OP_fpr=train_SVM_rbf_opt_OP_fpr, train_SVM_rbf_opt_OP_tpr=train_SVM_rbf_opt_OP_tpr,
#     val_SVM_rbf_opt_OP_fpr=val_SVM_rbf_opt_OP_fpr, val_SVM_rbf_opt_OP_tpr=val_SVM_rbf_opt_OP_tpr,
#     si_SVM_rbf_opt_OP_fpr=si_SVM_rbf_opt_OP_fpr, si_SVM_rbf_opt_OP_tpr=si_SVM_rbf_opt_OP_tpr,
#     SVM_rbf_opt_optimalOP_threshold=SVM_rbf_opt_optimalOP_threshold,
#     train_SVM_rbf_opt_optimalOP_fpr=train_SVM_rbf_opt_optimalOP_fpr, train_SVM_rbf_opt_optimalOP_tpr=train_SVM_rbf_opt_optimalOP_tpr,
#     val_SVM_rbf_opt_optimalOP_fpr=val_SVM_rbf_opt_optimalOP_fpr, val_SVM_rbf_opt_optimalOP_tpr=val_SVM_rbf_opt_optimalOP_tpr,
#     si_SVM_rbf_opt_optimalOP_fpr=si_SVM_rbf_opt_optimalOP_fpr, si_SVM_rbf_opt_optimalOP_tpr=si_SVM_rbf_opt_optimalOP_tpr)

# Load
SVM_rbf_optimal = joblib.load('SVM_rbf_optimal.pkl')
ROC_SVM_rbf_opt = np.load('ROC_SVM_rbf_opt.npz')
train_SVM_rbf_opt_score, val_SVM_rbf_opt_score, si_SVM_rbf_opt_score, \
        train_SVM_rbf_opt_fpr, train_SVM_rbf_opt_tpr, train_SVM_rbf_opt_thresholds, train_SVM_rbf_opt_roc_auc, \
        val_SVM_rbf_opt_fpr, val_SVM_rbf_opt_tpr, val_SVM_rbf_opt_thresholds, val_SVM_rbf_opt_roc_auc, \
        si_SVM_rbf_opt_fpr, si_SVM_rbf_opt_tpr, si_SVM_rbf_opt_thresholds, si_SVM_rbf_opt_roc_auc, \
        train_SVM_rbf_opt_OP_fpr, train_SVM_rbf_opt_OP_tpr, \
        val_SVM_rbf_opt_OP_fpr, val_SVM_rbf_opt_OP_tpr, \
        si_SVM_rbf_opt_OP_fpr, si_SVM_rbf_opt_OP_tpr, \
        train_SVM_rbf_opt_optimalOP_fpr, train_SVM_rbf_opt_optimalOP_tpr, \
        val_SVM_rbf_opt_optimalOP_fpr, val_SVM_rbf_opt_optimalOP_tpr, \
        si_SVM_rbf_opt_optimalOP_fpr, si_SVM_rbf_opt_optimalOP_tpr = \
    ROC_SVM_rbf_opt['train_SVM_rbf_opt_score'], ROC_SVM_rbf_opt['val_SVM_rbf_opt_score'], ROC_SVM_rbf_opt['si_SVM_rbf_opt_score'], \
        ROC_SVM_rbf_opt['train_SVM_rbf_opt_fpr'], ROC_SVM_rbf_opt['train_SVM_rbf_opt_tpr'], ROC_SVM_rbf_opt['train_SVM_rbf_opt_thresholds'], ROC_SVM_rbf_opt['train_SVM_rbf_opt_roc_auc'].item(), \
        ROC_SVM_rbf_opt['val_SVM_rbf_opt_fpr'], ROC_SVM_rbf_opt['val_SVM_rbf_opt_tpr'], ROC_SVM_rbf_opt['val_SVM_rbf_opt_thresholds'], ROC_SVM_rbf_opt['val_SVM_rbf_opt_roc_auc'].item(), \
        ROC_SVM_rbf_opt['si_SVM_rbf_opt_fpr'], ROC_SVM_rbf_opt['si_SVM_rbf_opt_tpr'], ROC_SVM_rbf_opt['si_SVM_rbf_opt_thresholds'], ROC_SVM_rbf_opt['si_SVM_rbf_opt_roc_auc'].item(), \
        ROC_SVM_rbf_opt['train_SVM_rbf_opt_OP_fpr'].item(), ROC_SVM_rbf_opt['train_SVM_rbf_opt_OP_tpr'].item(), \
        ROC_SVM_rbf_opt['val_SVM_rbf_opt_OP_fpr'].item(), ROC_SVM_rbf_opt['val_SVM_rbf_opt_OP_tpr'].item(), \
        ROC_SVM_rbf_opt['si_SVM_rbf_opt_OP_fpr'].item(), ROC_SVM_rbf_opt['si_SVM_rbf_opt_OP_tpr'].item(), \
        ROC_SVM_rbf_opt['train_SVM_rbf_opt_optimalOP_fpr'].item(), ROC_SVM_rbf_opt['train_SVM_rbf_opt_optimalOP_tpr'].item(), \
        ROC_SVM_rbf_opt['val_SVM_rbf_opt_optimalOP_fpr'].item(), ROC_SVM_rbf_opt['val_SVM_rbf_opt_optimalOP_tpr'].item(), \
        ROC_SVM_rbf_opt['si_SVM_rbf_opt_optimalOP_fpr'].item(), ROC_SVM_rbf_opt['si_SVM_rbf_opt_optimalOP_tpr'].item()


#############################################################
# COMPARISON OF ASSESSORS
#############################################################

# Train
plt.subplot(131)
# Critic
plt.plot(train_critic_fpr, train_critic_tpr, color='C0', label='C3DCritic; AUC={0:0.4f}'.format(train_critic_roc_auc))
plt.plot(train_critic_OP_fpr, train_critic_OP_tpr, color='C0', marker='x')
plt.plot(train_critic_optimalOP_fpr, train_critic_optimalOP_tpr, color='C0', marker='o')
# LogReg
plt.plot(train_logReg_unopt_fpr, train_logReg_unopt_tpr, color='C1', label='LogReg; AUC={0:0.4f}'.format(train_logReg_unopt_roc_auc))
plt.plot(train_logReg_unopt_OP_fpr, train_logReg_unopt_OP_tpr, color='C1', marker='x')
plt.plot(train_logReg_unopt_optimalOP_fpr, train_logReg_unopt_optimalOP_tpr, color='C1', marker='o')
# SVM Linear
plt.plot(train_SVM_linear_opt_fpr, train_SVM_linear_opt_tpr, color='C2', label='SVM - Linear; AUC={0:0.4f}'.format(train_SVM_linear_opt_roc_auc))
plt.plot(train_SVM_linear_opt_OP_fpr, train_SVM_linear_opt_OP_tpr, color='C2', marker='x')
plt.plot(train_SVM_linear_opt_optimalOP_fpr, train_SVM_linear_opt_optimalOP_tpr, color='C2', marker='o')
# SVM RBF
plt.plot(train_SVM_rbf_opt_fpr, train_SVM_rbf_opt_tpr, color='C3', label='SVM - RBF; AUC={0:0.4f}'.format(train_SVM_rbf_opt_roc_auc))
plt.plot(train_SVM_rbf_opt_OP_fpr, train_SVM_rbf_opt_OP_tpr, color='C3', marker='x')
plt.plot(train_SVM_rbf_opt_optimalOP_fpr, train_SVM_rbf_opt_optimalOP_tpr, color='C3', marker='o')
plt.legend(loc='lower right')
plt.xlabel('False positive rate')
plt.ylabel('True positive rate')
plt.title('Train')

# Val
plt.subplot(132)
# Critic
plt.plot(val_critic_fpr, val_critic_tpr, color='C0', label='C3DCritic; AUC={0:0.4f}'.format(val_critic_roc_auc))
plt.plot(val_critic_OP_fpr, val_critic_OP_tpr, color='C0', marker='x')
plt.plot(val_critic_optimalOP_fpr, val_critic_optimalOP_tpr, color='C0', marker='o')
# LogReg
plt.plot(val_logReg_unopt_fpr, val_logReg_unopt_tpr, color='C1', label='LogReg; AUC={0:0.4f}'.format(val_logReg_unopt_roc_auc))
plt.plot(val_logReg_unopt_OP_fpr, val_logReg_unopt_OP_tpr, color='C1', marker='x')
plt.plot(val_logReg_unopt_optimalOP_fpr, val_logReg_unopt_optimalOP_tpr, color='C1', marker='o')
# SVM Linear
plt.plot(val_SVM_linear_opt_fpr, val_SVM_linear_opt_tpr, color='C2', label='SVM - Linear; AUC={0:0.4f}'.format(val_SVM_linear_opt_roc_auc))
plt.plot(val_SVM_linear_opt_OP_fpr, val_SVM_linear_opt_OP_tpr, color='C2', marker='x')
plt.plot(val_SVM_linear_opt_optimalOP_fpr, val_SVM_linear_opt_optimalOP_tpr, color='C2', marker='o')
# SVM RBF
plt.plot(val_SVM_rbf_opt_fpr, val_SVM_rbf_opt_tpr, color='C3', label='SVM - RBF; AUC={0:0.4f}'.format(val_SVM_rbf_opt_roc_auc))
plt.plot(val_SVM_rbf_opt_OP_fpr, val_SVM_rbf_opt_OP_tpr, color='C3', marker='x')
plt.plot(val_SVM_rbf_opt_optimalOP_fpr, val_SVM_rbf_opt_optimalOP_tpr, color='C3', marker='o')
plt.legend(loc='lower right')
plt.xlabel('False positive rate')
plt.ylabel('True positive rate')
plt.title('Speaker-dependent Test')

# Si
plt.subplot(133)
# Critic
plt.plot(si_critic_fpr, si_critic_tpr, color='C0', label='C3DCritic; AUC={0:0.4f}'.format(si_critic_roc_auc))
plt.plot(si_critic_OP_fpr, si_critic_OP_tpr, color='C0', marker='x')
plt.plot(si_critic_optimalOP_fpr, si_critic_optimalOP_tpr, color='C0', marker='o')
# LogReg
plt.plot(si_logReg_unopt_fpr, si_logReg_unopt_tpr, color='C1', label='LogReg; AUC={0:0.4f}'.format(si_logReg_unopt_roc_auc))
plt.plot(si_logReg_unopt_OP_fpr, si_logReg_unopt_OP_tpr, color='C1', marker='x')
plt.plot(si_logReg_unopt_optimalOP_fpr, si_logReg_unopt_optimalOP_tpr, color='C1', marker='o')
# SVM Linear
plt.plot(si_SVM_linear_opt_fpr, si_SVM_linear_opt_tpr, color='C2', label='SVM - Linear; AUC={0:0.4f}'.format(si_SVM_linear_opt_roc_auc))
plt.plot(si_SVM_linear_opt_OP_fpr, si_SVM_linear_opt_OP_tpr, color='C2', marker='x')
plt.plot(si_SVM_linear_opt_optimalOP_fpr, si_SVM_linear_opt_optimalOP_tpr, color='C2', marker='o')
# SVM RBF
plt.plot(si_SVM_rbf_opt_fpr, si_SVM_rbf_opt_tpr, color='C3', label='SVM - RBF; AUC={0:0.4f}'.format(si_SVM_rbf_opt_roc_auc))
plt.plot(si_SVM_rbf_opt_OP_fpr, si_SVM_rbf_opt_OP_tpr, color='C3', marker='x')
plt.plot(si_SVM_rbf_opt_optimalOP_fpr, si_SVM_rbf_opt_optimalOP_tpr, color='C3', marker='o')
plt.legend(loc='lower right')
plt.xlabel('False positive rate')
plt.ylabel('True positive rate')
plt.title('Speaker-INdependent Test')

plt.suptitle("COMPARISON OF ASSESSORS ON BEST LIPREADER_PREDS")
plt.show()
