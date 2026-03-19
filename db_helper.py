"""
Database Helper Script - Query and manage diabetes prediction data
Usage: python db_helper.py
"""

from database import SessionLocal, PredictionRecord
from sqlalchemy import func
from datetime import datetime, timedelta

db = SessionLocal()

def print_header(title):
    print("\n" + "="*50)
    print(f"  {title}")
    print("="*50)

def option1_view_all():
    """View all predictions"""
    print_header("ALL PREDICTIONS")
    
    records = db.query(PredictionRecord).order_by(PredictionRecord.created_at.desc()).all()
    
    if not records:
        print("No predictions found in database.")
        return
    
    print(f"\nTotal Predictions: {len(records)}\n")
    
    for i, record in enumerate(records, 1):
        print(f"{i}. {record.user_name}")
        print(f"   Age: {record.age} | Gender: {record.gender}")
        print(f"   Result: {record.result} ({record.probability*100:.2f}% confidence)")
        print(f"   Date: {record.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

def option2_user_history():
    """View history for specific user"""
    print_header("USER PREDICTION HISTORY")
    
    user_name = input("Enter user name: ").strip()
    
    records = db.query(PredictionRecord).filter(
        PredictionRecord.user_name == user_name
    ).order_by(PredictionRecord.created_at.desc()).all()
    
    if not records:
        print(f"No predictions found for '{user_name}'")
        return
    
    print(f"\nHistory for {user_name}: {len(records)} predictions\n")
    
    diabetic_count = sum(1 for r in records if r.prediction == 1)
    
    for i, record in enumerate(records, 1):
        icon = "🔴" if record.result == "Diabetic" else "🟢"
        print(f"{i}. {icon} {record.result} ({record.probability*100:.2f}%)")
        print(f"   BMI: {record.bmi} | HbA1c: {record.hba1c_level}% | Glucose: {record.blood_glucose_level}")
        print(f"   {record.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    print(f"Summary: {diabetic_count} Diabetic, {len(records)-diabetic_count} Not Diabetic")

def option3_statistics():
    """View database statistics"""
    print_header("DATABASE STATISTICS")
    
    total = db.query(func.count(PredictionRecord.id)).scalar()
    
    if total == 0:
        print("No predictions in database yet.")
        return
    
    print(f"\nTotal Predictions: {total}")
    
    # Count by result
    diabetic = db.query(func.count(PredictionRecord.id)).filter(
        PredictionRecord.prediction == 1
    ).scalar()
    
    print(f"  Diabetic: {diabetic}")
    print(f"  Not Diabetic: {total - diabetic}")
    
    # Average probability
    avg_prob = db.query(func.avg(PredictionRecord.probability)).scalar()
    print(f"\nAverage Confidence: {avg_prob*100:.2f}%")
    
    # By gender
    print("\nBy Gender:")
    gender_stats = db.query(
        PredictionRecord.gender,
        func.count(PredictionRecord.id).label('count')
    ).group_by(PredictionRecord.gender).all()
    
    for gender, count in gender_stats:
        print(f"  {gender}: {count}")
    
    # Unique users
    unique_users = db.query(func.count(func.distinct(PredictionRecord.user_name))).scalar()
    print(f"\nUnique Users: {unique_users}")
    
    # Date range
    oldest = db.query(PredictionRecord).order_by(PredictionRecord.created_at.asc()).first()
    newest = db.query(PredictionRecord).order_by(PredictionRecord.created_at.desc()).first()
    
    if oldest and newest:
        print(f"\nDate Range:")
        print(f"  From: {oldest.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  To: {newest.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

def option4_export():
    """Export predictions to CSV"""
    print_header("EXPORT TO CSV")
    
    import csv
    
    records = db.query(PredictionRecord).all()
    
    if not records:
        print("No predictions to export.")
        return
    
    filename = "diabetes_predictions_export.csv"
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = [
            'user_name', 'gender', 'age', 'hypertension', 'heart_disease',
            'smoking_history', 'bmi', 'hba1c_level', 'blood_glucose_level',
            'prediction', 'result', 'probability', 'created_at'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for record in records:
            writer.writerow({
                'user_name': record.user_name,
                'gender': record.gender,
                'age': record.age,
                'hypertension': record.hypertension,
                'heart_disease': record.heart_disease,
                'smoking_history': record.smoking_history,
                'bmi': record.bmi,
                'hba1c_level': record.hba1c_level,
                'blood_glucose_level': record.blood_glucose_level,
                'prediction': record.prediction,
                'result': record.result,
                'probability': record.probability,
                'created_at': record.created_at
            })
    
    print(f"✓ Exported {len(records)} predictions to '{filename}'")

def option5_delete_user():
    """Delete records for a user"""
    print_header("DELETE USER RECORDS")
    
    user_name = input("Enter user name to delete: ").strip()
    confirm = input(f"Delete all {user_name}'s records? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        count = db.query(PredictionRecord).filter(
            PredictionRecord.user_name == user_name
        ).delete()
        
        db.commit()
        print(f"✓ Deleted {count} records for {user_name}")
    else:
        print("Cancelled.")

def option6_clear_all():
    """Clear entire database"""
    print_header("CLEAR DATABASE")
    
    confirm = input("⚠️  Delete ALL predictions? (type 'confirm' to proceed): ").strip()
    
    if confirm == 'confirm':
        double_confirm = input("This CANNOT be undone. Type 'yes' to confirm: ").strip().lower()
        
        if double_confirm == 'yes':
            count = db.query(PredictionRecord).delete()
            db.commit()
            print(f"✓ Deleted all {count} records")
        else:
            print("Cancelled.")
    else:
        print("Cancelled.")

def main():
    while True:
        print("\n" + "="*50)
        print("  DATABASE HELPER - Diabetes Predictions")
        print("="*50)
        print("\n1. View All Predictions")
        print("2. View User History")
        print("3. View Statistics")
        print("4. Export to CSV")
        print("5. Delete User Records")
        print("6. Clear Database")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-6): ").strip()
        
        if choice == '1':
            option1_view_all()
        elif choice == '2':
            option2_user_history()
        elif choice == '3':
            option3_statistics()
        elif choice == '4':
            option4_export()
        elif choice == '5':
            option5_delete_user()
        elif choice == '6':
            option6_clear_all()
        elif choice == '0':
            print("\nGoodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()
