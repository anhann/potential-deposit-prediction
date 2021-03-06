
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

"""### Summarisation"""

df=pd.read_csv('lixan23.csv')

df.describe(include='all')

"""Categorical data processing"""

df_cate = df.select_dtypes(include=['object']).copy()
df_numeric=df.select_dtypes(include=['int64']).copy()

df_binary=df_cate[['default','housing','loan','y']]
for i in df_binary.columns:
    df_binary.loc[df_cate[i]=='no',i]=0
    df_binary.loc[df_cate[i]=='yes',i]=1

from sklearn.preprocessing import LabelBinarizer
lb = LabelBinarizer()
def binary_convert(a):
    lb_results = lb.fit_transform(df_cate[a])
    df_onehot = pd.DataFrame(lb_results, columns=lb.classes_)
    for col in list(df_onehot.columns):
        df_onehot.rename(columns={col:(a+'_'+col)},inplace = True)
    return df_onehot
df_job_onehot=binary_convert('job')
df_mar_onehot=binary_convert('marital')
df_edu_onehot=binary_convert('education')
df_contact_onehot=binary_convert('contact')
df_pout_onehot=binary_convert('poutcome')

df_convert = pd.concat([df_numeric,df_binary, df_job_onehot,df_mar_onehot, 
                        df_edu_onehot, df_contact_onehot, df_pout_onehot], 
                       axis=1, sort=False)
df_cv=df_convert.astype('int64')

# Plotting heat map
corrmat = df_cv.corr()
corrmat.to_csv('corrmat.csv')
top_corr_features = corrmat.index
plt.figure(figsize=(50,50))
#plot heat map
g=sns.heatmap(df_cv[top_corr_features].corr(),annot=True,cmap="Blues",annot_kws={"size": 16})

# Correlation importance ranking
df_corr=df_cv.corr()[['y']]
df_corr['abs']=abs(df_corr['y'])
print(df_corr.sort_values(by='abs',ascending=False))
feat_imp_corr=df_corr.sort_values(by='abs',ascending=False).index

# Shortened heat map
df_cv_top=df_cv[['y','duration','poutcome_success','poutcome_unknown','contact_unknown','contact_cellular','housing','pdays']]
corrmat1 = df_cv_top.corr()
top_corr_features1 = corrmat1.index
plt.figure(figsize=(13,10))
#plot heat map
g=sns.heatmap(df_cv_top[top_corr_features1].corr(),annot=True,cmap="Blues", annot_kws={"size": 16})

# Variables with strong relationship
relationship=corrmat.where(abs(corrmat)>=0.3)
relationship.to_csv('relationship.csv')
relationship

"""### Exploration"""

Y=df_cv[['y']]
X=df_cv.loc[:,df_cv.columns!='y']
X_no_du=X.loc[:,X.columns!='duration']

"""Tree visualisation"""

from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
ct = DecisionTreeClassifier(min_samples_leaf=30, max_depth=10, random_state=42)

ct.fit(X,Y)
fn=['age', 'balance', 'day', 'duration', 'campaign', 'pdays', 'previous',
       'default', 'housing', 'loan', 'job_admin.', 'job_blue-collar',
       'job_entrepreneur', 'job_housemaid', 'job_management', 'job_retired',
       'job_self-employed', 'job_services', 'job_student', 'job_technician',
       'job_unemployed', 'job_unknown', 'marital_divorced', 'marital_married',
       'marital_single', 'education_primary', 'education_secondary',
       'education_tertiary', 'education_unknown', 'contact_cellular',
       'contact_telephone', 'contact_unknown', 'poutcome_failure',
       'poutcome_other', 'poutcome_success', 'poutcome_unknown','pday_1']
cn=['no','yes']
fig, axes = plt.subplots(nrows = 1,ncols = 1,figsize = (10,10), dpi=2000)
tree.plot_tree(ct,
               feature_names = fn, 
               class_names=cn,
               filled = True)

ct.fit(X_no_du,Y)
fn=['age', 'balance', 'day', 'campaign', 'pdays', 'previous', 'default',
       'housing', 'loan', 'job_admin.', 'job_blue-collar', 'job_entrepreneur',
       'job_housemaid', 'job_management', 'job_retired', 'job_self-employed',
       'job_services', 'job_student', 'job_technician', 'job_unemployed',
       'job_unknown', 'marital_divorced', 'marital_married', 'marital_single',
       'education_primary', 'education_secondary', 'education_tertiary',
       'education_unknown', 'contact_cellular', 'contact_telephone',
       'contact_unknown', 'poutcome_failure', 'poutcome_other',
       'poutcome_success', 'poutcome_unknown']
cn=['no','yes']
fig, axes = plt.subplots(nrows = 1,ncols = 1,figsize = (10,10), dpi=800)
tree.plot_tree(ct,
               feature_names = fn, 
               class_names=cn,
               filled = True)

"""Feature importance"""

#Tuning Tree with precision
from sklearn import feature_selection 
from sklearn import decomposition, datasets
from sklearn.model_selection import GridSearchCV
ct1=DecisionTreeClassifier(random_state=42)
criterion = ['gini', 'entropy']
max_depth = list(range(1,10))
min_samples_leaf=list(range(1,100))
parameters = dict(criterion=criterion,
                  max_depth=max_depth,
                 min_samples_leaf=min_samples_leaf)
ct_GS = GridSearchCV(ct1, parameters, scoring='precision',cv=5)
ct_GS.fit(X_no_du, Y)
print(ct_GS.best_params_)
print(ct_GS.best_estimator_)
print(ct_GS.best_score_)

# Feature importance for precision
ct_pre=DecisionTreeClassifier(ccp_alpha=0.0, class_weight=None, criterion='entropy',
                       max_depth=4, max_features=None, max_leaf_nodes=None,
                       min_impurity_decrease=0.0, min_impurity_split=None,
                       min_samples_leaf=26, min_samples_split=2,
                       min_weight_fraction_leaf=0.0, presort='deprecated',
                       random_state=42, splitter='best')
ct_pre.fit(X_no_du,Y)
feat_importance = ct_pre.tree_.compute_feature_importances(normalize=False)
feat_imp_dict = dict(zip(X_no_du.columns, ct_pre.feature_importances_))
feat_imp = pd.DataFrame.from_dict(feat_imp_dict, orient='index')
feat_imp.rename(columns = {0:'FeatureImportance'}, inplace = True)
feat_imp_pre=feat_imp.sort_values(by=['FeatureImportance'], ascending=False)
feat_imp_pre

# Checking precision, recall and f1 with tree_pre
from sklearn.model_selection import cross_val_score
print('precision:', np.mean(cross_val_score(ct_pre,X=X_no_du,y=Y, scoring='precision',cv=5)))
print('recall:', np.mean(cross_val_score(ct_pre,X=X_no_du,y=Y, scoring='recall',cv=5)))
print('f1:', np.mean(cross_val_score(ct_pre,X=X_no_du,y=Y, scoring='f1',cv=5)))
print('accuracy:', np.mean(cross_val_score(ct_pre,X=X_no_du,y=Y, scoring='accuracy',cv=5)))

# Checking precision, recall and f1 with tree_pre when only include 'poutcome_success' and 'housing'
X_temp=X[['poutcome_success','housing']]
ct_temp=DecisionTreeClassifier(random_state=42)
print('precision:', np.mean(cross_val_score(ct_temp,X=X_temp,y=Y, scoring='precision',cv=5)))
print('recall:', np.mean(cross_val_score(ct_temp,X=X_temp,y=Y, scoring='recall',cv=5)))
print('f1:', np.mean(cross_val_score(ct_temp,X=X_temp,y=Y, scoring='f1',cv=5)))
print('accuracy:', np.mean(cross_val_score(ct_temp,X=X_temp,y=Y, scoring='accuracy',cv=5)))

#Tuning Tree with recall
criterion = ['gini', 'entropy']
max_depth = list(range(1,40))
min_samples_leaf=list(range(1,100))
parameters = dict(criterion=criterion,
                  max_depth=max_depth,
                 min_samples_leaf=min_samples_leaf)
ct_GS = GridSearchCV(ct1, parameters, scoring='recall',cv=5)
ct_GS.fit(X_no_du, Y)
print(ct_GS.best_params_)
print(ct_GS.best_estimator_)
print(ct_GS.best_score_)

# Feature importance for recall
ct_re=DecisionTreeClassifier(ccp_alpha=0.0, class_weight=None, criterion='entropy',
                       max_depth=28, max_features=None, max_leaf_nodes=None,
                       min_impurity_decrease=0.0, min_impurity_split=None,
                       min_samples_leaf=1, min_samples_split=2,
                       min_weight_fraction_leaf=0.0, presort='deprecated',
                       random_state=42, splitter='best')
ct_re.fit(X_no_du,Y)
feat_importance = ct_re.tree_.compute_feature_importances(normalize=False)
feat_imp_dict = dict(zip(X_no_du.columns, ct_re.feature_importances_))
feat_imp = pd.DataFrame.from_dict(feat_imp_dict, orient='index')
feat_imp.rename(columns = {0:'FeatureImportance'}, inplace = True)
feat_imp_re=feat_imp.sort_values(by=['FeatureImportance'], ascending=False)
feat_imp_re

# Checking precision, recall and f1 with tree_re
print('precision:', np.mean(cross_val_score(ct_re,X=X_no_du,y=Y, scoring='precision',cv=5)))
print('recall:', np.mean(cross_val_score(ct_re,X=X_no_du,y=Y, scoring='recall',cv=5)))
print('f1:', np.mean(cross_val_score(ct_re,X=X_no_du,y=Y, scoring='f1',cv=5)))
print('accuracy:', np.mean(cross_val_score(ct_re,X=X_no_du,y=Y, scoring='accuracy',cv=5)))

"""### Model evaluation

Precision Optimisation
"""

from sklearn.model_selection import train_test_split
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3, random_state=42)
X_train_min=X_train[['poutcome_success','housing']]
X_test_min=X_test[['poutcome_success','housing']]

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import neighbors
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import CategoricalNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier

knn = neighbors.KNeighborsClassifier()
dm = DummyClassifier(strategy='most_frequent',random_state=42)
rf= RandomForestClassifier(random_state=42)
lr=LogisticRegression()
gnb=GaussianNB()
cnb=CategoricalNB()

# Tuning Tree
criterion = ['gini', 'entropy']
max_depth = list(range(1,10))
min_samples_leaf=list(range(1,100))
parameters = dict(criterion=criterion,
                  max_depth=max_depth,
                 min_samples_leaf=min_samples_leaf)
ct_GS = GridSearchCV(ct1, parameters, scoring='precision',cv=5)
ct_GS.fit(X_train_min, Y_train)
print(ct_GS.best_params_)
print(ct_GS.best_estimator_)
print(ct_GS.best_score_)

# Tuning kNN - scaling no require as all input are binary
n_neighbors = list(range(1,30))
parameters = dict(n_neighbors=n_neighbors)
knn_GS = GridSearchCV(knn, parameters,scoring='precision', cv=5)
knn_GS.fit(X_train_min,Y_train)
print(knn_GS.best_params_)
print(knn_GS.best_estimator_)
print(knn_GS.best_score_)

# Tuning RF
n_estimators = list(range(5,100,5))
max_depth=list(range(2,15))
parameters = dict(n_estimators = n_estimators, max_depth=max_depth)
rf=RandomForestClassifier(random_state=42)
rf_GS = GridSearchCV(rf, parameters, cv = 5, scoring='precision')
rf_GS.fit(X_train_min, Y_train)
print(rf_GS.best_params_)
print(rf_GS.best_estimator_)
print(rf_GS.best_score_)

# Tuned model
ct_tuned=DecisionTreeClassifier(ccp_alpha=0.0, class_weight=None, criterion='gini',
                       max_depth=2, max_features=None, max_leaf_nodes=None,
                       min_impurity_decrease=0.0, min_impurity_split=None,
                       min_samples_leaf=1, min_samples_split=2,
                       min_weight_fraction_leaf=0.0, presort='deprecated',
                       random_state=42, splitter='best')
knn_tuned=neighbors.KNeighborsClassifier(algorithm='auto', leaf_size=30, metric='minkowski', n_neighbors=7, p=2,
                     weights='uniform')
rf_tuned=RandomForestClassifier(bootstrap=True, ccp_alpha=0.0, class_weight=None,
                       criterion='gini', max_depth=2, max_features='auto',
                       max_leaf_nodes=None, max_samples=None,
                       min_impurity_decrease=0.0, min_impurity_split=None,
                       min_samples_leaf=1, min_samples_split=2,
                       min_weight_fraction_leaf=0.0, n_estimators=5,
                       n_jobs=None, oob_score=False, random_state=42, verbose=0,
                       warm_start=False)

ct_tuned.fit(X_train_min,Y_train)
rf_tuned.fit(X_train_min,Y_train)
knn_tuned.fit(X_train_min,Y_train)
lr.fit(X_train_min,Y_train)
cnb.fit(X_train_min,Y_train)
dm.fit(X_train_min,Y_train)

from sklearn.metrics import plot_confusion_matrix
plot_confusion_matrix(lr, X=X_test_min, y_true=Y_test, values_format='d', cmap='Blues')
plot_confusion_matrix(ct_tuned, X=X_test_min, y_true=Y_test, values_format='d', cmap='Blues')
plot_confusion_matrix(rf_tuned, X=X_test_min, y_true=Y_test, values_format='d', cmap='Blues')
plot_confusion_matrix(knn_tuned, X=X_test_min, y_true=Y_test, values_format='d', cmap='Blues')
plot_confusion_matrix(cnb, X=X_test_min, y_true=Y_test, values_format='d', cmap='Blues')
plot_confusion_matrix(dm, X=X_test_min, y_true=Y_test, values_format='d', cmap='Greys')

from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import accuracy_score
print('lr:', precision_score(Y_test,lr.predict(X_test_min)), recall_score(Y_test,lr.predict(X_test_min)),accuracy_score(Y_test,lr.predict(X_test_min)))
print('ct:', precision_score(Y_test,ct_tuned.predict(X_test_min)), recall_score(Y_test,ct_tuned.predict(X_test_min)),accuracy_score(Y_test,ct_tuned.predict(X_test_min)))
print('rf:', precision_score(Y_test,rf_tuned.predict(X_test_min)), recall_score(Y_test,rf_tuned.predict(X_test_min)),accuracy_score(Y_test,rf_tuned.predict(X_test_min)))
print('knn:', precision_score(Y_test,knn_tuned.predict(X_test_min)), recall_score(Y_test,knn_tuned.predict(X_test_min)),accuracy_score(Y_test,knn_tuned.predict(X_test_min)))
print('nb:', precision_score(Y_test,cnb.predict(X_test_min)), recall_score(Y_test,cnb.predict(X_test_min)),accuracy_score(Y_test,cnb.predict(X_test_min)))
print('dm:', precision_score(Y_test,dm.predict(X_test_min)), recall_score(Y_test,dm.predict(X_test_min)),accuracy_score(Y_test,dm.predict(X_test_min)))

"""Trade-off Cost Evaluation"""

# Trade-off with X min
from sklearn.metrics import plot_precision_recall_curve
plot_precision_recall_curve(lr, X_test_min, Y_test, ax=plt.gca(),name = 'LR')
plot_precision_recall_curve(cnb, X_test_min, Y_test, ax=plt.gca(),name = 'NB')
plot_precision_recall_curve(ct_tuned, X_test_min, Y_test, ax=plt.gca(),name = 'CT')
plot_precision_recall_curve(rf_tuned, X_test_min, Y_test, ax=plt.gca(),name = 'RF')
plot_precision_recall_curve(knn_tuned, X_test_min, Y_test, ax=plt.gca(),name = 'KNN')
plot_precision_recall_curve(dm, X_test_min, Y_test, ax=plt.gca(),name = 'DM')
plt.legend(bbox_to_anchor=(1, 1))

from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
folds = KFold(n_splits=5, shuffle=True, random_state=42)

ct=DecisionTreeClassifier(random_state=42)
rf=RandomForestClassifier(random_state=42)
name=list(range(1,36))
lr_f1=[]
ct_f1=[]
nb_f1=[]
rf_f1=[]
lr_pre=[]
ct_pre=[]
nb_pre=[]
rf_pre=[]
lr_re=[]
ct_re=[]
nb_re=[]
rf_re=[]

for i in feat_imp_pre.index:
    if i=='poutcome_success':
        X_temp=X[[i]]
    else:
        X_temp[i]=X[i]
    lr_scores1 = cross_val_score(lr, X_temp, Y, scoring='f1', cv=folds)
    lr_f1.append(np.mean(lr_scores1))
    lr_scores2 = cross_val_score(lr, X_temp, Y, scoring='precision', cv=folds)
    lr_pre.append(np.mean(lr_scores2))
    lr_scores3 = cross_val_score(lr, X_temp, Y, scoring='recall', cv=folds)
    lr_re.append(np.mean(lr_scores3))   
    
    ct_scores1 = cross_val_score(ct, X_temp, Y, scoring='f1', cv=folds)
    ct_f1.append(np.mean(ct_scores1))
    ct_scores2 = cross_val_score(ct, X_temp, Y, scoring='precision', cv=folds)
    ct_pre.append(np.mean(ct_scores2))
    ct_scores3 = cross_val_score(ct, X_temp, Y, scoring='recall', cv=folds)
    ct_re.append(np.mean(ct_scores3))     
    
    nb_scores1 = cross_val_score(gnb, X_temp, Y, scoring='f1', cv=folds)
    nb_f1.append(np.mean(nb_scores1))
    nb_scores2 = cross_val_score(gnb, X_temp, Y, scoring='precision', cv=folds)
    nb_pre.append(np.mean(nb_scores2))
    nb_scores3 = cross_val_score(gnb, X_temp, Y, scoring='recall', cv=folds)
    nb_re.append(np.mean(nb_scores3))   
    
    rf_scores1 = cross_val_score(rf, X_temp, Y, scoring='f1', cv=folds)
    rf_f1.append(np.mean(rf_scores1))
    rf_scores2 = cross_val_score(rf, X_temp, Y, scoring='precision', cv=folds)
    rf_pre.append(np.mean(rf_scores2))
    rf_scores3 = cross_val_score(rf, X_temp, Y, scoring='recall', cv=folds)
    rf_re.append(np.mean(rf_scores3))

# Trade-off table
table = {'added_features': feat_imp_pre.index,'ct_pre': ct_pre, 'ct_re': ct_re,'ct_f1':ct_f1,
        'nb_pre': nb_pre, 'nb_re': nb_re,'nb_f1':nb_f1,
        'rf_pre': rf_pre, 'rf_re': rf_re,'rf_f1':rf_f1,
        'lr_pre': lr_pre, 'lr_re': lr_re,'lr_f1':lr_f1,}
trade_off_table = pd.DataFrame(data=table)
trade_off_table.to_csv('trade_off.csv')
trade_off_table

# Plot trade-off precision vs recall
name=list(range(1,36))
plt.plot(name, lr_re,'r-')
plt.plot(name, ct_re,'b-')
plt.plot(name, nb_re,'g-')
plt.plot(name, rf_re,'y-')
plt.plot(name, lr_pre,'r--')
plt.plot(name, ct_pre,'b--')
plt.plot(name, nb_pre,'g--')
plt.plot(name, rf_pre,'y--')

# Plot f1
plt.plot(name, lr_f1,'r*')
plt.plot(name, ct_f1,'b*')
plt.plot(name, nb_f1,'g*')
plt.plot(name, rf_f1,'y*')

