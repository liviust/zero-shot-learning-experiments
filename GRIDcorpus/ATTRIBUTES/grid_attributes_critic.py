import numpy as np
import optunity
import optunity.metrics

from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
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

si_dirs = grid_basics['si_dirs']; si_dirs = si_dirs[:12000]
si_word_numbers = grid_basics['si_word_numbers']; si_word_numbers = si_word_numbers[:12000]
si_word_idx = grid_basics['si_word_idx']; si_word_idx = si_word_idx[:12000]

#############################################################
# LOAD ATTRIBUTES
#############################################################

train_grid_attributes = np.load('train_grid_attributes_matrix.npy')
val_grid_attributes = np.load('val_grid_attributes_matrix.npy')
si_grid_attributes = np.load('si_grid_attributes_matrix.npy'); si_grid_attributes = si_grid_attributes[:12000]

# Normalization
train_grid_attributes_norm = (train_grid_attributes - train_grid_attributes.min(0)) / train_grid_attributes.ptp(0)
val_grid_attributes_norm = (val_grid_attributes - val_grid_attributes.min(0)) / val_grid_attributes.ptp(0)
si_grid_attributes_norm = (si_grid_attributes - si_grid_attributes.min(0)) / si_grid_attributes.ptp(0); si_grid_attributes_norm[:, 1] = 1.

# Leave out the first three attributes
train_matrix = train_grid_attributes_norm[:, 3:]
val_matrix = val_grid_attributes_norm[:, 3:]
si_matrix = si_grid_attributes_norm[:, 3:]

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

lipreader_preds_wordidx_and_correctorwrong = np.load('lipreader_preds_wordidx_and_correctorwrong.npy').item()

train_lipreader_preds_word_idx = lipreader_preds_wordidx_and_correctorwrong['train_lipreader_preds_word_idx']
val_lipreader_preds_word_idx = lipreader_preds_wordidx_and_correctorwrong['val_lipreader_preds_word_idx']
si_lipreader_preds_word_idx = lipreader_preds_wordidx_and_correctorwrong['si_lipreader_preds_word_idx']; si_lipreader_preds_word_idx = si_lipreader_preds_word_idx[:12000]

train_lipreader_preds_correct_or_wrong = lipreader_preds_wordidx_and_correctorwrong['train_lipreader_preds_correct_or_wrong']
val_lipreader_preds_correct_or_wrong = lipreader_preds_wordidx_and_correctorwrong['val_lipreader_preds_correct_or_wrong']
si_lipreader_preds_correct_or_wrong = lipreader_preds_wordidx_and_correctorwrong['si_lipreader_preds_correct_or_wrong']; si_lipreader_preds_correct_or_wrong = si_lipreader_preds_correct_or_wrong[:12000]

# >>> np.sum(train_lipreader_preds_correct_or_wrong)/len(train_lipreader_preds_correct_or_wrong)
# 0.92210520716983135
# >>> np.sum(val_lipreader_preds_correct_or_wrong)/len(val_lipreader_preds_correct_or_wrong)
# 0.92036242250834521
# >>> np.sum(si_lipreader_preds_correct_or_wrong)/len(si_lipreader_preds_correct_or_wrong)
# 0.38550000000000001

#############################################################
# LOAD LIPREADER PREDS
#############################################################

lipreader_preds = np.load('lipreader_preds.npz')

train_lipreader_preds = lipreader_preds['train_lipreader_preds']
val_lipreader_preds = lipreader_preds['val_lipreader_preds']
si_lipreader_preds = lipreader_preds['si_lipreader_preds']; si_lipreader_preds = si_lipreader_preds[:12000]

#############################################################
# LOAD CRITIC PREDS
#############################################################

critic_preds = np.load('critic_preds.npz')

train_critic_preds = critic_preds['train_critic_preds']
val_critic_preds = critic_preds['val_critic_preds']
si_critic_preds = critic_preds['si_critic_preds']; si_critic_preds = si_critic_preds[:12000]

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
    # train_lipreader_fpr_op=train_lipreader_fpr_op, train_lipreader_tpr_op=train_lipreader_tpr_op,
    # val_lipreader_fpr_op=val_lipreader_fpr_op, val_lipreader_tpr_op=val_lipreader_tpr_op,
    # si_lipreader_fpr_op=si_lipreader_fpr_op, si_lipreader_tpr_op=si_lipreader_tpr_op)

#############################################################
# CRITIC ROC
#############################################################

# CONFUSION MATRIX, OPERATING POINT
# Train
train_critic_tn, train_critic_fp, train_critic_fn, train_critic_tp = confusion_matrix(train_lipreader_preds_correct_or_wrong, train_critic_preds > .5).ravel()
train_critic_fpr_op = train_critic_fp/(train_critic_fp + train_critic_tn)
train_critic_tpr_op = train_critic_tp/(train_critic_tp + train_critic_fn)
# Val
val_critic_tn, val_critic_fp, val_critic_fn, val_critic_tp = confusion_matrix(val_lipreader_preds_correct_or_wrong, val_critic_preds > .5).ravel()
val_critic_fpr_op = val_critic_fp/(val_critic_fp + val_critic_tn)
val_critic_tpr_op = val_critic_tp/(val_critic_tp + val_critic_fn)
# Si
si_critic_tn, si_critic_fp, si_critic_fn, si_critic_tp = confusion_matrix(si_lipreader_preds_correct_or_wrong, si_critic_preds > .5).ravel()
si_critic_fpr_op = si_critic_fp/(si_critic_fp + si_critic_tn)
si_critic_tpr_op = si_critic_tp/(si_critic_tp + si_critic_fn)

# Acc
# >>> (train_critic_tp + train_critic_tn)/(train_critic_tp + train_critic_fp + train_critic_fn + train_critic_tn)
# 0.64650816445933723
# >>> (val_critic_tp + val_critic_tn)/(val_critic_tp + val_critic_fp + val_critic_fn + val_critic_tn)
# 0.64854554124940389
# >>> (si_critic_tp + si_critic_tn)/(si_critic_tp + si_critic_fp + si_critic_fn + si_critic_tn)
# 0.6323333333333333

# Compute ROC
train_critic_fpr, train_critic_tpr, train_critic_thresholds, train_critic_roc_auc, \
        val_critic_fpr, val_critic_tpr, val_critic_thresholds, val_critic_roc_auc, \
        si_critic_fpr, si_critic_tpr, si_critic_thresholds, si_critic_roc_auc = \
    compute_ROC_grid_singleclass(train_lipreader_preds_correct_or_wrong, train_critic_preds,
        val_lipreader_preds_correct_or_wrong, val_critic_preds,
        si_lipreader_preds_correct_or_wrong, si_critic_preds,
        train_critic_fpr_op, train_critic_tpr_op,
        val_critic_fpr_op, val_critic_tpr_op,
        si_critic_fpr_op, si_critic_tpr_op,
        savePlot=True, showPlot=True,
        plot_title='ROC curve of C3DCritic')

train_critic_roc_auc, val_critic_roc_auc, si_critic_roc_auc
# (0.73482362164374793, 0.74337826936799978, 0.64395556254427311)

np.savez('ROC_C3DCritic',
    train_critic_fpr=train_critic_fpr, train_critic_tpr=train_critic_tpr, train_critic_thresholds=train_critic_thresholds, train_critic_roc_auc=train_critic_roc_auc,
    val_critic_fpr=val_critic_fpr, val_critic_tpr=val_critic_tpr, val_critic_thresholds=val_critic_thresholds, val_critic_roc_auc=val_critic_roc_auc,
    si_critic_fpr=si_critic_fpr, si_critic_tpr=si_critic_tpr, si_critic_thresholds=si_critic_thresholds, si_critic_roc_auc=si_critic_roc_auc,
    train_critic_fpr_op=train_critic_fpr_op, train_critic_tpr_op=train_critic_tpr_op,
    val_critic_fpr_op=val_critic_fpr_op, val_critic_tpr_op=val_critic_tpr_op,
    si_critic_fpr_op=si_critic_fpr_op, si_critic_tpr_op=si_critic_tpr_op)


#############################################################
# LOGISTIC REGRESSOR ROC
#############################################################

# logReg = LogisticRegression()
# logReg.fit(train_matrix, train_lipreader_preds_correct_or_wrong)

# # Save
# joblib.dump(logReg, 'logReg_unopt.pkl', compress=3) 

# # Acc
# logReg.score(train_matrix, train_lipreader_preds_correct_or_wrong)
# logReg.score(val_matrix, val_lipreader_preds_correct_or_wrong)
# logReg.score(si_matrix, si_lipreader_preds_correct_or_wrong)
# # >>> # Acc
# # ... logReg.score(train_matrix, train_lipreader_preds_correct_or_wrong)
# # 0.92226477315036437
# # >>> logReg.score(val_matrix, val_lipreader_preds_correct_or_wrong)
# # 0.92083929422985222
# # >>> logReg.score(si_matrix, si_lipreader_preds_correct_or_wrong)
# # 0.38700000000000001

# # CONFUSION MATRIX, OPERATING POINT
# train_logReg_unopt_fpr_op, train_logReg_unopt_tpr_op, \
#         val_logReg_unopt_fpr_op, val_logReg_unopt_tpr_op, \
#         si_logReg_unopt_fpr_op, si_logReg_unopt_tpr_op = \
#     calc_grid_operating_points(logReg,
#         train_lipreader_preds_correct_or_wrong, val_lipreader_preds_correct_or_wrong, si_lipreader_preds_correct_or_wrong,
#         train_matrix, val_matrix, si_matrix)

# # Scores
# train_logReg_unopt_score = logReg.decision_function(train_matrix)
# val_logReg_unopt_score = logReg.decision_function(val_matrix)
# si_logReg_unopt_score = logReg.decision_function(si_matrix)

# # Compute ROC
# train_logReg_unopt_fpr, train_logReg_unopt_tpr, train_logReg_unopt_thresholds, train_logReg_unopt_roc_auc, \
#         val_logReg_unopt_fpr, val_logReg_unopt_tpr, val_logReg_unopt_thresholds, val_logReg_unopt_roc_auc, \
#         si_logReg_unopt_fpr, si_logReg_unopt_tpr, si_logReg_unopt_thresholds, si_logReg_unopt_roc_auc = \
#     compute_ROC_grid_singleclass(train_lipreader_preds_correct_or_wrong, train_logReg_unopt_score,
#         val_lipreader_preds_correct_or_wrong, val_logReg_unopt_score,
#         si_lipreader_preds_correct_or_wrong, si_logReg_unopt_score,
#         train_logReg_unopt_fpr_op, train_logReg_unopt_tpr_op,
#         val_logReg_unopt_fpr_op, val_logReg_unopt_tpr_op,
#         si_logReg_unopt_fpr_op, si_logReg_unopt_tpr_op,
#         savePlot=True, showPlot=True,
#         plot_title='ROC curve of Logistic Regressor (unoptimized)')

# train_logReg_unopt_roc_auc, val_logReg_unopt_roc_auc, si_logReg_unopt_roc_auc
# # (0.83961853740044889, 0.85645031181160991, 0.62133158287065327)

# np.savez('ROC_logReg_unopt',
#     train_logReg_unopt_score=train_logReg_unopt_score, val_logReg_unopt_score=val_logReg_unopt_score, si_logReg_unopt_score=si_logReg_unopt_score,
#     train_logReg_unopt_fpr=train_logReg_unopt_fpr, train_logReg_unopt_tpr=train_logReg_unopt_tpr, train_logReg_unopt_thresholds=train_logReg_unopt_thresholds, train_logReg_unopt_roc_auc=train_logReg_unopt_roc_auc,
#     val_logReg_unopt_fpr=val_logReg_unopt_fpr, val_logReg_unopt_tpr=val_logReg_unopt_tpr, val_logReg_unopt_thresholds=val_logReg_unopt_thresholds, val_logReg_unopt_roc_auc=val_logReg_unopt_roc_auc,
#     si_logReg_unopt_fpr=si_logReg_unopt_fpr, si_logReg_unopt_tpr=si_logReg_unopt_tpr, si_logReg_unopt_thresholds=si_logReg_unopt_thresholds, si_logReg_unopt_roc_auc=si_logReg_unopt_roc_auc,
#     train_logReg_unopt_fpr_op=train_logReg_unopt_fpr_op, train_logReg_unopt_tpr_op=train_logReg_unopt_tpr_op,
#     val_logReg_unopt_fpr_op=val_logReg_unopt_fpr_op, val_logReg_unopt_tpr_op=val_logReg_unopt_tpr_op,
#     si_logReg_unopt_fpr_op=si_logReg_unopt_fpr_op, si_logReg_unopt_tpr_op=si_logReg_unopt_tpr_op)


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
# train_logReg_unopt_fpr_op, train_logReg_unopt_tpr_op, \
#         val_logReg_unopt_fpr_op, val_logReg_unopt_tpr_op, \
#         si_logReg_unopt_fpr_op, si_logReg_unopt_tpr_op = \
#     calc_grid_operating_points(logReg,
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
#         train_logReg_unopt_fpr_op, train_logReg_unopt_tpr_op,
#         val_logReg_unopt_fpr_op, val_logReg_unopt_tpr_op,
#         si_logReg_unopt_fpr_op, si_logReg_unopt_tpr_op,
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
# train_SVM_linear_opt_fpr_op, train_SVM_linear_opt_tpr_op, \
#         val_SVM_linear_opt_fpr_op, val_SVM_linear_opt_tpr_op, \
#         si_SVM_linear_opt_fpr_op, si_SVM_linear_opt_tpr_op = \
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
#         train_SVM_linear_opt_fpr_op, train_SVM_linear_opt_tpr_op,
#         val_SVM_linear_opt_fpr_op, val_SVM_linear_opt_tpr_op,
#         si_SVM_linear_opt_fpr_op, si_SVM_linear_opt_tpr_op,
#         savePlot=True, showPlot=True,
#         plot_title='ROC curve of linear SVM (optimized)')

# np.savez('ROC_SVM_linear_opt',
#     train_SVM_linear_opt_score=train_SVM_linear_opt_score, val_SVM_linear_opt_score=val_SVM_linear_opt_score, si_SVM_linear_opt_score=si_SVM_linear_opt_score,
#     train_SVM_linear_opt_fpr=train_SVM_linear_opt_fpr, train_SVM_linear_opt_tpr=train_SVM_linear_opt_tpr, train_SVM_linear_opt_thresholds=train_SVM_linear_opt_thresholds, train_SVM_linear_opt_roc_auc=train_SVM_linear_opt_roc_auc,
#     val_SVM_linear_opt_fpr=val_SVM_linear_opt_fpr, val_SVM_linear_opt_tpr=val_SVM_linear_opt_tpr, val_SVM_linear_opt_thresholds=val_SVM_linear_opt_thresholds, val_SVM_linear_opt_roc_auc=val_SVM_linear_opt_roc_auc,
#     si_SVM_linear_opt_fpr=si_SVM_linear_opt_fpr, si_SVM_linear_opt_tpr=si_SVM_linear_opt_tpr, si_SVM_linear_opt_thresholds=si_SVM_linear_opt_thresholds, si_SVM_linear_opt_roc_auc=si_SVM_linear_opt_roc_auc,
#     train_SVM_linear_opt_fpr_op=train_SVM_linear_opt_fpr_op, train_SVM_linear_opt_tpr_op=train_SVM_linear_opt_tpr_op,
#     val_SVM_linear_opt_fpr_op=val_SVM_linear_opt_fpr_op, val_SVM_linear_opt_tpr_op=val_SVM_linear_opt_tpr_op,
#     si_SVM_linear_opt_fpr_op=si_SVM_linear_opt_fpr_op, si_SVM_linear_opt_tpr_op=si_SVM_linear_opt_tpr_op)

# Load
SVM_linear_optimal = joblib.load('SVM_linear_optimal.pkl')
ROC_SVM_linear_opt = np.load('ROC_SVM_linear_opt.npz')
train_SVM_linear_opt_score, val_SVM_linear_opt_score, si_SVM_linear_opt_score, \
        train_SVM_linear_opt_fpr, train_SVM_linear_opt_tpr, train_SVM_linear_opt_thresholds, train_SVM_linear_opt_roc_auc, \
        val_SVM_linear_opt_fpr, val_SVM_linear_opt_tpr, val_SVM_linear_opt_thresholds, val_SVM_linear_opt_roc_auc, \
        si_SVM_linear_opt_fpr, si_SVM_linear_opt_tpr, si_SVM_linear_opt_thresholds, si_SVM_linear_opt_roc_auc , \
        train_SVM_linear_opt_fpr_op, train_SVM_linear_opt_tpr_op, \
        val_SVM_linear_opt_fpr_op, val_SVM_linear_opt_tpr_op, \
        si_SVM_linear_opt_fpr_op, si_SVM_linear_opt_tpr_op = \
    ROC_SVM_linear_opt['train_SVM_linear_opt_score'], ROC_SVM_linear_opt['val_SVM_linear_opt_score'], ROC_SVM_linear_opt['si_SVM_linear_opt_score'], \
        ROC_SVM_linear_opt['train_SVM_linear_opt_fpr'], ROC_SVM_linear_opt['train_SVM_linear_opt_tpr'], ROC_SVM_linear_opt['train_SVM_linear_opt_thresholds'], ROC_SVM_linear_opt['train_SVM_linear_opt_roc_auc'].item(), \
        ROC_SVM_linear_opt['val_SVM_linear_opt_fpr'], ROC_SVM_linear_opt['val_SVM_linear_opt_tpr'], ROC_SVM_linear_opt['val_SVM_linear_opt_thresholds'], ROC_SVM_linear_opt['val_SVM_linear_opt_roc_auc'].item(), \
        ROC_SVM_linear_opt['si_SVM_linear_opt_fpr'], ROC_SVM_linear_opt['si_SVM_linear_opt_tpr'], ROC_SVM_linear_opt['si_SVM_linear_opt_thresholds'], ROC_SVM_linear_opt['si_SVM_linear_opt_roc_auc'].item(), \
        ROC_SVM_linear_opt['train_SVM_linear_opt_fpr_op'].item(), ROC_SVM_linear_opt['train_SVM_linear_opt_tpr_op'].item(), \
        ROC_SVM_linear_opt['val_SVM_linear_opt_fpr_op'].item(), ROC_SVM_linear_opt['val_SVM_linear_opt_tpr_op'].item(), \
        ROC_SVM_linear_opt['si_SVM_linear_opt_fpr_op'].item(), ROC_SVM_linear_opt['si_SVM_linear_opt_tpr_op'].item()


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
# train_SVM_rbf_opt_fpr_op, train_SVM_rbf_opt_tpr_op, \
#         val_SVM_rbf_opt_fpr_op, val_SVM_rbf_opt_tpr_op, \
#         si_SVM_rbf_opt_fpr_op, si_SVM_rbf_opt_tpr_op = \
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
#         train_SVM_rbf_opt_fpr_op, train_SVM_rbf_opt_tpr_op,
#         val_SVM_rbf_opt_fpr_op, val_SVM_rbf_opt_tpr_op,
#         si_SVM_rbf_opt_fpr_op, si_SVM_rbf_opt_tpr_op,
#         savePlot=False, showPlot=False,
#         plot_title='ROC curve of RBF SVM optimized')

# np.savez('ROC_SVM_rbf_opt',
#     train_SVM_rbf_opt_score=train_SVM_rbf_opt_score, val_SVM_rbf_opt_score=val_SVM_rbf_opt_score, si_SVM_rbf_opt_score=si_SVM_rbf_opt_score,
#     train_SVM_rbf_opt_fpr=train_SVM_rbf_opt_fpr, train_SVM_rbf_opt_tpr=train_SVM_rbf_opt_tpr, train_SVM_rbf_opt_thresholds=train_SVM_rbf_opt_thresholds, train_SVM_rbf_opt_roc_auc=train_SVM_rbf_opt_roc_auc,
#     val_SVM_rbf_opt_fpr=val_SVM_rbf_opt_fpr, val_SVM_rbf_opt_tpr=val_SVM_rbf_opt_tpr, val_SVM_rbf_opt_thresholds=val_SVM_rbf_opt_thresholds, val_SVM_rbf_opt_roc_auc=val_SVM_rbf_opt_roc_auc,
#     si_SVM_rbf_opt_fpr=si_SVM_rbf_opt_fpr, si_SVM_rbf_opt_tpr=si_SVM_rbf_opt_tpr, si_SVM_rbf_opt_thresholds=si_SVM_rbf_opt_thresholds, si_SVM_rbf_opt_roc_auc=si_SVM_rbf_opt_roc_auc,
#     train_SVM_rbf_opt_fpr_op=train_SVM_rbf_opt_fpr_op, train_SVM_rbf_opt_tpr_op=train_SVM_rbf_opt_tpr_op,
#     val_SVM_rbf_opt_fpr_op=val_SVM_rbf_opt_fpr_op, val_SVM_rbf_opt_tpr_op=val_SVM_rbf_opt_tpr_op,
#     si_SVM_rbf_opt_fpr_op=si_SVM_rbf_opt_fpr_op, si_SVM_rbf_opt_tpr_op=si_SVM_rbf_opt_tpr_op)

# Load
SVM_rbf_optimal = joblib.load('SVM_rbf_optimal.pkl')
ROC_SVM_rbf_opt = np.load('ROC_SVM_rbf_opt.npz')
train_SVM_rbf_opt_score, val_SVM_rbf_opt_score, si_SVM_rbf_opt_score, \
        train_SVM_rbf_opt_fpr, train_SVM_rbf_opt_tpr, train_SVM_rbf_opt_thresholds, train_SVM_rbf_opt_roc_auc, \
        val_SVM_rbf_opt_fpr, val_SVM_rbf_opt_tpr, val_SVM_rbf_opt_thresholds, val_SVM_rbf_opt_roc_auc, \
        si_SVM_rbf_opt_fpr, si_SVM_rbf_opt_tpr, si_SVM_rbf_opt_thresholds, si_SVM_rbf_opt_roc_auc, \
        train_SVM_rbf_opt_fpr_op, train_SVM_rbf_opt_tpr_op, \
        val_SVM_rbf_opt_fpr_op, val_SVM_rbf_opt_tpr_op, \
        si_SVM_rbf_opt_fpr_op, si_SVM_rbf_opt_tpr_op = \
    ROC_SVM_rbf_opt['train_SVM_rbf_opt_score'], ROC_SVM_rbf_opt['val_SVM_rbf_opt_score'], ROC_SVM_rbf_opt['si_SVM_rbf_opt_score'], \
        ROC_SVM_rbf_opt['train_SVM_rbf_opt_fpr'], ROC_SVM_rbf_opt['train_SVM_rbf_opt_tpr'], ROC_SVM_rbf_opt['train_SVM_rbf_opt_thresholds'], ROC_SVM_rbf_opt['train_SVM_rbf_opt_roc_auc'].item(), \
        ROC_SVM_rbf_opt['val_SVM_rbf_opt_fpr'], ROC_SVM_rbf_opt['val_SVM_rbf_opt_tpr'], ROC_SVM_rbf_opt['val_SVM_rbf_opt_thresholds'], ROC_SVM_rbf_opt['val_SVM_rbf_opt_roc_auc'].item(), \
        ROC_SVM_rbf_opt['si_SVM_rbf_opt_fpr'], ROC_SVM_rbf_opt['si_SVM_rbf_opt_tpr'], ROC_SVM_rbf_opt['si_SVM_rbf_opt_thresholds'], ROC_SVM_rbf_opt['si_SVM_rbf_opt_roc_auc'].item(), \
        ROC_SVM_rbf_opt['train_SVM_rbf_opt_fpr_op'].item(), ROC_SVM_rbf_opt['train_SVM_rbf_opt_tpr_op'].item(), \
        ROC_SVM_rbf_opt['val_SVM_rbf_opt_fpr_op'].item(), ROC_SVM_rbf_opt['val_SVM_rbf_opt_tpr_op'].item(), \
        ROC_SVM_rbf_opt['si_SVM_rbf_opt_fpr_op'].item(), ROC_SVM_rbf_opt['si_SVM_rbf_opt_tpr_op'].item()

# plt.plot(train_SVM_rbf_opt_fpr, train_SVM_rbf_opt_tpr, color='C0', label='train; AUC={0:0.4f}'.format(train_SVM_rbf_opt_roc_auc))
# plt.plot(val_SVM_rbf_opt_fpr, val_SVM_rbf_opt_tpr, color='C1', label='val; AUC={0:0.4f}'.format(val_SVM_rbf_opt_roc_auc))
# plt.plot(si_SVM_rbf_opt_fpr, si_SVM_rbf_opt_tpr, color='C2', label='si; AUC={0:0.4f}'.format(si_SVM_rbf_opt_roc_auc))
# plt.plot(train_SVM_rbf_opt_fpr_op, train_SVM_rbf_opt_tpr_op, color='C0', marker='x')
# plt.plot(val_SVM_rbf_opt_fpr_op, val_SVM_rbf_opt_tpr_op, color='C1', marker='x')
# plt.plot(si_SVM_rbf_opt_fpr_op, si_SVM_rbf_opt_tpr_op, color='C2', marker='x')
# plt.legend(loc='lower right')
# plt.xlabel('False positive rate')
# plt.ylabel('True positive rate')
# plt.title('ROC curve of RBF SVM optimized')
# plt.show()

#############################################################
# LIPREADER SELF-TRAIN 10%
#############################################################






