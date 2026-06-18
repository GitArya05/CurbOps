import json
import re
import os

results = []

def check1():
    try:
        with open('CurbOps_Pipeline/build_cbm_dataset.py', 'r', encoding='utf-8') as f:
            content = f.read()
        if 'MapmyIndia' in content or 'mmi' in content.lower():
            if 'junction_name' in content and 'latitude' in content and 'longitude' in content:
                # We need to see if it updates the DataFrame
                return 'FAIL: Script does not appear to actually perform MapmyIndia enrichment or merge it properly.'
            else:
                return 'FAIL: MapmyIndia logic missing.'
        return 'FAIL: MapmyIndia logic missing entirely.'
    except Exception as e:
        return f'FAIL: Error checking build_cbm_dataset.py - {e}'

def check2():
    try:
        with open('CurbOps_Pipeline/run_clustering.py', 'r', encoding='utf-8') as f:
            content = f.read()
        if 'safe_peak_factor = 0.5 + 0.5 * peak_hour_ratio' in content:
            return 'PASS'
        return 'FAIL: Dampening formula not found in run_clustering.py.'
    except Exception as e:
        return f'FAIL: Error checking run_clustering.py - {e}'

def check3():
    try:
        with open('documentation/clustering_walkthrough.md', 'r', encoding='utf-8') as f:
            content = f.read()
        if '7-10 AM' in content and '5-7 PM' in content and 'artifact' in content.lower():
            return 'PASS'
        return 'FAIL: Documentation does not mention the 7-10 AM / 5-7 PM window or the artifact caveat.'
    except Exception as e:
        return f'FAIL: Error checking documentation - {e}'

def check4():
    try:
        with open('CurbOps_Pipeline/dataset/zone_summary.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'action_tier' not in data[0]:
            return 'FAIL: action_tier missing from zone_summary.json.'
        
        with open('CurbOps_Pipeline/dataset/zones.geojson', 'r', encoding='utf-8') as f:
            geo_data = json.load(f)
        if 'action_tier' not in geo_data['features'][0]['properties']:
            return 'FAIL: action_tier missing from zones.geojson.'
        
        return 'PASS'
    except Exception as e:
        return f'FAIL: Error checking json outputs - {e}'

def check5():
    try:
        with open('CurbOps_Pipeline/run_clustering.py', 'r', encoding='utf-8') as f:
            content = f.read()
        if 'sort_values(by=\"priority_score\"' in content or 'sort_values(\"priority_score\"' in content or 'sort_values(by=''priority_score''' in content:
            # Check json
            with open('CurbOps_Pipeline/dataset/zone_summary.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            p_scores = [d.get('priority_score', 0) for d in data]
            is_sorted = all(p_scores[i] >= p_scores[i+1] for i in range(len(p_scores)-1))
            if is_sorted:
                return 'PASS'
            else:
                return 'FAIL: Json is not sorted by priority_score descending.'
        else:
            return 'FAIL: Sorting by priority_score not found in run_clustering.py.'
    except Exception as e:
        return f'FAIL: Error checking sorting - {e}'

def check6():
    try:
        with open('CurbOps_Pipeline/build_cbm_dataset.py', 'r', encoding='utf-8') as f:
            content = f.read()
        if 'CLIENT_ID' in content or 'CLIENT_SECRET' in content:
            if 'os.getenv' in content or 'secrets.txt' in content or 'os.environ' in content:
                return 'PASS'
            else:
                return 'FAIL: Hardcoded credentials might still be present.'
        else:
            return 'FAIL: CLIENT_ID/SECRET not referenced.'
    except Exception as e:
        return f'FAIL: Error checking credentials - {e}'

print(f"Check 1: {check1()}")
print(f"Check 2: {check2()}")
print(f"Check 3: {check3()}")
print(f"Check 4: {check4()}")
print(f"Check 5: {check5()}")
print(f"Check 6: {check6()}")
