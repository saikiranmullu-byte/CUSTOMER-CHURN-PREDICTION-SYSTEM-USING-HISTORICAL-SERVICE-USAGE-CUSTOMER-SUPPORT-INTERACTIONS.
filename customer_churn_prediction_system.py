"""
Customer Churn Prediction System
Predicts customer attrition using historical service usage and behavioral analytics
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, roc_curve
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.svm import SVC
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

def generate_customer_data(n_samples=2000, random_state=42):
    """Generate synthetic customer churn data"""
    np.random.seed(random_state)
    
    data = []
    
    for i in range(n_samples):
        # Customer demographics
        customer_id = f'CUST{i+1:06d}'
        age = np.random.randint(18, 75)
        tenure_months = np.random.randint(1, 72)
        
        # Service usage patterns
        monthly_charges = np.random.uniform(20, 150)
        total_charges = monthly_charges * tenure_months
        
        # Usage metrics
        data_usage_gb = np.random.uniform(0, 100)
        call_minutes = np.random.uniform(0, 1000)
        sms_count = np.random.randint(0, 500)
        
        # Customer support interactions
        support_tickets = np.random.randint(0, 20)
        complaint_count = np.random.randint(0, 10)
        resolution_time_days = np.random.uniform(0, 30) if complaint_count > 0 else 0
        
        # Payment behavior
        payment_method = np.random.choice(['Credit Card', 'Bank Transfer', 'Check', 'Electronic Check'])
        paperless_billing = np.random.choice([0, 1], p=[0.3, 0.7])
        late_payments = np.random.randint(0, 5)
        
        # Engagement metrics
        contract_type = np.random.choice(['Month-to-month', 'One year', 'Two year'])
        internet_service = np.random.choice(['Fiber optic', 'DSL', 'No'])
        online_security = np.random.choice([0, 1], p=[0.5, 0.5])
        tech_support = np.random.choice([0, 1], p=[0.6, 0.4])
        
        # Churn determination based on factors
        churn_probability = 0.0
        
        # High support tickets indicate dissatisfaction
        churn_probability += support_tickets * 0.02
        
        # Complaints increase churn risk
        churn_probability += complaint_count * 0.05
        
        # Month-to-month contracts have higher churn
        if contract_type == 'Month-to-month':
            churn_probability += 0.3
        elif contract_type == 'One year':
            churn_probability += 0.1
        
        # Short tenure increases churn
        if tenure_months < 6:
            churn_probability += 0.2
        elif tenure_months < 12:
            churn_probability += 0.1
        
        # Late payments indicate financial issues
        churn_probability += late_payments * 0.08
        
        # High charges increase churn
        if monthly_charges > 100:
            churn_probability += 0.15
        
        # Tech support reduces churn
        if tech_support == 1:
            churn_probability -= 0.1
        
        # Online security reduces churn
        if online_security == 1:
            churn_probability -= 0.05
        
        # Fiber optic service reduces churn
        if internet_service == 'Fiber optic':
            churn_probability -= 0.05
        
        # Clamp probability
        churn_probability = max(0, min(1, churn_probability))
        
        # Determine churn
        churn = 1 if np.random.random() < churn_probability else 0
        
        data.append({
            'Customer_ID': customer_id,
            'Age': age,
            'Tenure_Months': tenure_months,
            'Monthly_Charges': monthly_charges,
            'Total_Charges': total_charges,
            'Data_Usage_GB': data_usage_gb,
            'Call_Minutes': call_minutes,
            'SMS_Count': sms_count,
            'Support_Tickets': support_tickets,
            'Complaint_Count': complaint_count,
            'Resolution_Time_Days': resolution_time_days,
            'Late_Payments': late_payments,
            'Paperless_Billing': paperless_billing,
            'Contract_Type': contract_type,
            'Internet_Service': internet_service,
            'Online_Security': online_security,
            'Tech_Support': tech_support,
            'Churn': churn
        })
    
    return pd.DataFrame(data)

def prepare_features(df):
    """Prepare features for modeling"""
    df_copy = df.copy()
    
    # Encode categorical features
    contract_encoded = pd.get_dummies(df_copy['Contract_Type'], prefix='contract')
    internet_encoded = pd.get_dummies(df_copy['Internet_Service'], prefix='internet')
    
    # Select numeric features
    numeric_features = df_copy[['Age', 'Tenure_Months', 'Monthly_Charges', 'Total_Charges',
                                'Data_Usage_GB', 'Call_Minutes', 'SMS_Count', 'Support_Tickets',
                                'Complaint_Count', 'Resolution_Time_Days', 'Late_Payments',
                                'Paperless_Billing', 'Online_Security', 'Tech_Support']]
    
    # Combine all features
    X = pd.concat([numeric_features, contract_encoded, internet_encoded], axis=1)
    y = df_copy['Churn']
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns)
    
    return X_scaled, y, scaler

def train_models(X_train, X_test, y_train, y_test):
    """Train multiple classification models"""
    models = {}
    results = []
    predictions = {}
    
    # Logistic Regression
    print("Training Logistic Regression...")
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    y_proba_lr = lr.predict_proba(X_test)[:, 1]
    
    models['Logistic Regression'] = lr
    predictions['Logistic Regression'] = y_pred_lr
    results.append({
        'Model': 'Logistic Regression',
        'Accuracy': accuracy_score(y_test, y_pred_lr),
        'Precision': precision_score(y_test, y_pred_lr),
        'Recall': recall_score(y_test, y_pred_lr),
        'F1_Score': f1_score(y_test, y_pred_lr),
        'ROC_AUC': roc_auc_score(y_test, y_proba_lr)
    })
    
    # Random Forest
    print("Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    y_proba_rf = rf.predict_proba(X_test)[:, 1]
    
    models['Random Forest'] = rf
    predictions['Random Forest'] = y_pred_rf
    results.append({
        'Model': 'Random Forest',
        'Accuracy': accuracy_score(y_test, y_pred_rf),
        'Precision': precision_score(y_test, y_pred_rf),
        'Recall': recall_score(y_test, y_pred_rf),
        'F1_Score': f1_score(y_test, y_pred_rf),
        'ROC_AUC': roc_auc_score(y_test, y_proba_rf)
    })
    
    # Gradient Boosting
    print("Training Gradient Boosting...")
    gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
    gb.fit(X_train, y_train)
    y_pred_gb = gb.predict(X_test)
    y_proba_gb = gb.predict_proba(X_test)[:, 1]
    
    models['Gradient Boosting'] = gb
    predictions['Gradient Boosting'] = y_pred_gb
    results.append({
        'Model': 'Gradient Boosting',
        'Accuracy': accuracy_score(y_test, y_pred_gb),
        'Precision': precision_score(y_test, y_pred_gb),
        'Recall': recall_score(y_test, y_pred_gb),
        'F1_Score': f1_score(y_test, y_pred_gb),
        'ROC_AUC': roc_auc_score(y_test, y_proba_gb)
    })
    
    # AdaBoost
    print("Training AdaBoost...")
    ab = AdaBoostClassifier(n_estimators=100, random_state=42)
    ab.fit(X_train, y_train)
    y_pred_ab = ab.predict(X_test)
    y_proba_ab = ab.predict_proba(X_test)[:, 1]
    
    models['AdaBoost'] = ab
    predictions['AdaBoost'] = y_pred_ab
    results.append({
        'Model': 'AdaBoost',
        'Accuracy': accuracy_score(y_test, y_pred_ab),
        'Precision': precision_score(y_test, y_pred_ab),
        'Recall': recall_score(y_test, y_pred_ab),
        'F1_Score': f1_score(y_test, y_pred_ab),
        'ROC_AUC': roc_auc_score(y_test, y_proba_ab)
    })
    
    return models, pd.DataFrame(results), y_test, predictions, y_proba_gb

def plot_churn_distribution(df):
    """Plot churn distribution and characteristics"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Churn distribution
    churn_counts = df['Churn'].value_counts()
    colors = ['#2ecc71', '#e74c3c']
    axes[0, 0].bar(['Retained', 'Churned'], churn_counts.values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0, 0].set_ylabel('Customer Count', fontsize=11, fontweight='bold')
    axes[0, 0].set_title('Customer Churn Distribution', fontsize=12, fontweight='bold')
    axes[0, 0].grid(axis='y', alpha=0.3)
    for i, v in enumerate(churn_counts.values):
        axes[0, 0].text(i, v + 20, str(v), ha='center', fontweight='bold')
    
    # Tenure vs churn
    for churn in [0, 1]:
        data = df[df['Churn'] == churn]['Tenure_Months']
        axes[0, 1].hist(data, bins=20, alpha=0.6, label=['Retained', 'Churned'][churn], color=colors[churn], edgecolor='black')
    axes[0, 1].set_xlabel('Tenure (Months)', fontsize=11, fontweight='bold')
    axes[0, 1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[0, 1].set_title('Tenure Distribution by Churn Status', fontsize=12, fontweight='bold')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)
    
    # Contract type vs churn
    contract_churn = pd.crosstab(df['Contract_Type'], df['Churn'])
    contract_churn.plot(kind='bar', ax=axes[1, 0], color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1, 0].set_xlabel('Contract Type', fontsize=11, fontweight='bold')
    axes[1, 0].set_ylabel('Customer Count', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('Churn by Contract Type', fontsize=12, fontweight='bold')
    axes[1, 0].legend(['Retained', 'Churned'], loc='upper right')
    axes[1, 0].grid(axis='y', alpha=0.3)
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Monthly charges vs churn
    for churn in [0, 1]:
        data = df[df['Churn'] == churn]['Monthly_Charges']
        axes[1, 1].hist(data, bins=20, alpha=0.6, label=['Retained', 'Churned'][churn], color=colors[churn], edgecolor='black')
    axes[1, 1].set_xlabel('Monthly Charges ($)', fontsize=11, fontweight='bold')
    axes[1, 1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[1, 1].set_title('Monthly Charges Distribution by Churn Status', fontsize=12, fontweight='bold')
    axes[1, 1].legend()
    axes[1, 1].grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/churn_distribution.png', dpi=300, bbox_inches='tight')
    print("Saved: churn_distribution.png")
    plt.close()

def plot_model_comparison(results_df):
    """Plot model performance comparison"""
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1_Score', 'ROC_AUC']
    
    for idx, metric in enumerate(metrics):
        row = idx // 3
        col = idx % 3
        
        axes[row, col].bar(results_df['Model'], results_df[metric], color=colors, alpha=0.8, 
                          edgecolor='black', linewidth=1.5)
        axes[row, col].set_ylabel(metric, fontsize=11, fontweight='bold')
        axes[row, col].set_title(f'{metric} Comparison', fontsize=12, fontweight='bold')
        axes[row, col].set_ylim([0, 1.1])
        axes[row, col].grid(axis='y', alpha=0.3)
        axes[row, col].tick_params(axis='x', rotation=45)
        
        for i, v in enumerate(results_df[metric]):
            axes[row, col].text(i, v + 0.02, f'{v:.3f}', ha='center', fontweight='bold', fontsize=9)
    
    # Remove extra subplot
    fig.delaxes(axes[1, 2])
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/churn_model_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved: churn_model_comparison.png")
    plt.close()

def plot_confusion_matrices(y_test, predictions):
    """Plot confusion matrices"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    for idx, (model_name, y_pred) in enumerate(predictions.items()):
        row = idx // 2
        col = idx % 2
        
        cm = confusion_matrix(y_test, y_pred)
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[row, col], 
                   cbar=False, annot_kws={'fontsize': 12, 'fontweight': 'bold'},
                   xticklabels=['Retained', 'Churned'], yticklabels=['Retained', 'Churned'])
        axes[row, col].set_ylabel('Actual', fontsize=11, fontweight='bold')
        axes[row, col].set_xlabel('Predicted', fontsize=11, fontweight='bold')
        axes[row, col].set_title(f'{model_name} Confusion Matrix', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/churn_confusion_matrices.png', dpi=300, bbox_inches='tight')
    print("Saved: churn_confusion_matrices.png")
    plt.close()

def plot_feature_importance(models):
    """Plot feature importance"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Random Forest
    rf_model = models['Random Forest']
    importances = rf_model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1][:10]
    feature_names = [f'Feature_{i}' for i in range(len(importances))]
    
    axes[0].barh(np.array(feature_names)[sorted_idx], importances[sorted_idx], color='#3498db', 
                alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[0].set_xlabel('Importance', fontsize=11, fontweight='bold')
    axes[0].set_title('Random Forest Feature Importance', fontsize=12, fontweight='bold')
    axes[0].grid(axis='x', alpha=0.3)
    
    # Gradient Boosting
    gb_model = models['Gradient Boosting']
    importances = gb_model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1][:10]
    
    axes[1].barh(np.array(feature_names)[sorted_idx], importances[sorted_idx], color='#e74c3c', 
                alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1].set_xlabel('Importance', fontsize=11, fontweight='bold')
    axes[1].set_title('Gradient Boosting Feature Importance', fontsize=12, fontweight='bold')
    axes[1].grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/churn_feature_importance.png', dpi=300, bbox_inches='tight')
    print("Saved: churn_feature_importance.png")
    plt.close()

def plot_roc_curves(y_test, y_proba_gb, models, X_test):
    """Plot ROC curves"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    colors_roc = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
    
    for idx, (model_name, model) in enumerate(models.items()):
        if hasattr(model, 'predict_proba'):
            y_proba = model.predict_proba(X_test)[:, 1] if model_name != 'Gradient Boosting' else y_proba_gb
            fpr, tpr, _ = roc_curve(y_test, y_proba)
            auc = roc_auc_score(y_test, y_proba)
            ax.plot(fpr, tpr, label=f'{model_name} (AUC = {auc:.3f})', linewidth=2.5, color=colors_roc[idx])
    
    ax.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Random Classifier')
    ax.set_xlabel('False Positive Rate', fontsize=11, fontweight='bold')
    ax.set_ylabel('True Positive Rate', fontsize=11, fontweight='bold')
    ax.set_title('ROC Curves Comparison', fontsize=12, fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/churn_roc_curves.png', dpi=300, bbox_inches='tight')
    print("Saved: churn_roc_curves.png")
    plt.close()

def plot_support_analysis(df):
    """Plot support and complaint analysis"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Support tickets vs churn
    for churn in [0, 1]:
        data = df[df['Churn'] == churn]['Support_Tickets']
        axes[0, 0].hist(data, bins=15, alpha=0.6, label=['Retained', 'Churned'][churn], 
                       color=['#2ecc71', '#e74c3c'][churn], edgecolor='black')
    axes[0, 0].set_xlabel('Support Tickets', fontsize=11, fontweight='bold')
    axes[0, 0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[0, 0].set_title('Support Tickets by Churn Status', fontsize=12, fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)
    
    # Complaints vs churn
    for churn in [0, 1]:
        data = df[df['Churn'] == churn]['Complaint_Count']
        axes[0, 1].hist(data, bins=10, alpha=0.6, label=['Retained', 'Churned'][churn], 
                       color=['#2ecc71', '#e74c3c'][churn], edgecolor='black')
    axes[0, 1].set_xlabel('Complaint Count', fontsize=11, fontweight='bold')
    axes[0, 1].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[0, 1].set_title('Complaints by Churn Status', fontsize=12, fontweight='bold')
    axes[0, 1].legend()
    axes[0, 1].grid(alpha=0.3)
    
    # Late payments vs churn
    for churn in [0, 1]:
        data = df[df['Churn'] == churn]['Late_Payments']
        axes[1, 0].hist(data, bins=5, alpha=0.6, label=['Retained', 'Churned'][churn], 
                       color=['#2ecc71', '#e74c3c'][churn], edgecolor='black')
    axes[1, 0].set_xlabel('Late Payments', fontsize=11, fontweight='bold')
    axes[1, 0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes[1, 0].set_title('Late Payments by Churn Status', fontsize=12, fontweight='bold')
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)
    
    # Tech support adoption
    tech_support_churn = pd.crosstab(df['Tech_Support'], df['Churn'])
    tech_support_churn.plot(kind='bar', ax=axes[1, 1], color=['#2ecc71', '#e74c3c'], 
                           alpha=0.8, edgecolor='black', linewidth=1.5)
    axes[1, 1].set_xlabel('Tech Support (0=No, 1=Yes)', fontsize=11, fontweight='bold')
    axes[1, 1].set_ylabel('Customer Count', fontsize=11, fontweight='bold')
    axes[1, 1].set_title('Tech Support Adoption by Churn Status', fontsize=12, fontweight='bold')
    axes[1, 1].legend(['Retained', 'Churned'])
    axes[1, 1].grid(axis='y', alpha=0.3)
    axes[1, 1].tick_params(axis='x', rotation=0)
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/churn_support_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved: churn_support_analysis.png")
    plt.close()

def main():
    print("="*80)
    print("CUSTOMER CHURN PREDICTION SYSTEM")
    print("="*80)
    
    # Generate dataset
    print("\n[1] Generating customer data...")
    df = generate_customer_data(n_samples=2000)
    df.to_csv('/home/ubuntu/customer_churn_data.csv', index=False)
    print(f"Dataset generated: {len(df)} records")
    print(f"Churned customers: {(df['Churn'] == 1).sum()} ({(df['Churn'] == 1).sum()/len(df)*100:.1f}%)")
    print(f"Retained customers: {(df['Churn'] == 0).sum()} ({(df['Churn'] == 0).sum()/len(df)*100:.1f}%)")
    
    # Prepare features
    print("\n[2] Preparing features...")
    X, y, scaler = prepare_features(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Training set: {len(X_train)}, Test set: {len(X_test)}")
    
    # Train models
    print("\n[3] Training classification models...")
    models, results_df, y_test, predictions, y_proba_gb = train_models(X_train, X_test, y_train, y_test)
    results_df.to_csv('/home/ubuntu/churn_model_results.csv', index=False)
    print("\nModel Results:")
    print(results_df.to_string(index=False))
    
    # Generate visualizations
    print("\n[4] Generating visualizations...")
    plot_churn_distribution(df)
    plot_model_comparison(results_df)
    plot_confusion_matrices(y_test, predictions)
    plot_feature_importance(models)
    plot_roc_curves(y_test, y_proba_gb, models, X_test)
    plot_support_analysis(df)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE - All visualizations saved")
    print("="*80)

if __name__ == "__main__":
    main()
