"""Test script for exploratory analysis integration."""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_full_flow():
    """Test complete upload → explore → get session flow."""
    
    print("=" * 60)
    print("Testing Exploratory Analysis Integration")
    print("=" * 60)
    
    # Step 1: Upload CSV
    print("\n1. Uploading sample_data.csv...")
    with open("sample_data.csv", "rb") as f:
        files = {"file": ("sample_data.csv", f, "text/csv")}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.text}")
        return
    
    upload_data = response.json()
    session_id = upload_data["session_id"]
    print(f"✅ Upload successful!")
    print(f"   Session ID: {session_id}")
    print(f"   Filename: {upload_data['filename']}")
    print(f"   Row count: {upload_data['row_count']}")
    print(f"   Status: {upload_data['status']}")
    
    # Step 2: Run exploration
    print(f"\n2. Running exploration on session {session_id}...")
    response = requests.post(f"{BASE_URL}/explore/{session_id}")
    
    if response.status_code != 200:
        print(f"❌ Exploration failed: {response.text}")
        return
    
    explore_data = response.json()
    print(f"✅ Exploration complete!")
    print(f"   Status: {explore_data['status']}")
    
    # Display Data DNA summary
    data_dna = explore_data["data_dna"]
    print(f"\n📊 Data DNA Summary:")
    print(f"   Rows: {data_dna['row_count']}")
    print(f"   Columns: {data_dna['col_count']}")
    print(f"   Health Score: {data_dna['health']['score']}")
    print(f"   Completeness: {data_dna['health']['completeness']}%")
    
    print(f"\n🔍 Detected Patterns:")
    for pattern in data_dna['detected_patterns']:
        print(f"   • {pattern}")
    
    print(f"\n💡 Suggested Queries:")
    for i, query in enumerate(data_dna['suggested_queries'], 1):
        print(f"   {i}. {query}")
    
    print(f"\n📈 Column Profiles:")
    for col in data_dna['columns'][:3]:  # Show first 3
        print(f"   • {col['name']} ({col['type']})")
        print(f"     - Null: {col['null_pct']}%")
        print(f"     - Unique: {col['unique_count']}")
        if col['type'] == 'numeric':
            print(f"     - Mean: {col.get('mean')}")
            print(f"     - Outliers: {col.get('outlier_count')}")
        elif col['type'] == 'categorical':
            print(f"     - Top values: {col.get('top_values')}")
    
    if data_dna['correlations']:
        print(f"\n🔗 Correlations:")
        for corr in data_dna['correlations'][:3]:  # Show first 3
            print(f"   • {corr['col_a']} ↔ {corr['col_b']}: r={corr['pearson_r']} ({corr['strength']})")
    
    if data_dna['datetime_info']:
        print(f"\n📅 Datetime Info:")
        dt_info = data_dna['datetime_info']
        print(f"   • Column: {dt_info['column']}")
        print(f"   • Peak Hour: {dt_info['peak_hour']}:00")
        print(f"   • Peak Day: {dt_info['peak_day']}")
        print(f"   • Span: {dt_info['span_days']} days")
    
    # Step 3: Get session
    print(f"\n3. Fetching session details...")
    response = requests.get(f"{BASE_URL}/session/{session_id}")
    
    if response.status_code != 200:
        print(f"❌ Get session failed: {response.text}")
        return
    
    session_data = response.json()
    print(f"✅ Session retrieved!")
    print(f"   Status: {session_data['status']}")
    print(f"   Data DNA present: {'data_dna' in session_data and session_data['data_dna'] is not None}")
    
    # Save full Data DNA to file
    print(f"\n4. Saving full Data DNA to 'data_dna_output.json'...")
    with open("data_dna_output.json", "w") as f:
        json.dump(data_dna, f, indent=2)
    print(f"✅ Saved!")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check Supabase → sessions table → data_dna column")
    print("2. Review data_dna_output.json for full structure")
    print("3. Test frontend integration")

if __name__ == "__main__":
    try:
        test_full_flow()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
