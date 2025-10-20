#!/usr/bin/env python3
"""
Performance test script for LawGPT optimizations
"""

import requests
import time
import json

def test_lawgpt_performance():
    """Test LawGPT performance improvements"""
    url = "http://localhost:5000/api/query"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token"  # This will be ignored for testing
    }
    
    test_queries = [
        "What is Article 370?",
        "Explain Section 498A of IPC",
        "What are consumer rights in India?",
        "How to file a PIL in Supreme Court?",
        "What is Article 370?",  # Repeat to test cache
        "Explain Section 498A of IPC",  # Repeat to test cache
    ]
    
    print("🚀 Testing LawGPT Performance Optimizations")
    print("=" * 60)
    
    total_time = 0
    cache_hits = 0
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        
        start_time = time.time()
        try:
            response = requests.post(url, json={"query": query}, headers=headers)
            end_time = time.time()
            
            response_time = end_time - start_time
            total_time += response_time
            
            if response.status_code == 200:
                data = response.json()
                lawgpt_response = data.get('lawgpt', '')
                
                # Check if response was from cache (simplified check)
                if "cached" in lawgpt_response.lower() or response_time < 0.1:
                    cache_hits += 1
                    print(f"✅ Cache Hit - Response time: {response_time:.2f}s")
                else:
                    print(f"🔄 Generated - Response time: {response_time:.2f}s")
                
                print(f"Response length: {len(lawgpt_response)} characters")
                
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Performance summary
    avg_time = total_time / len(test_queries)
    cache_hit_rate = (cache_hits / len(test_queries)) * 100
    
    print(f"\n📊 Performance Summary:")
    print(f"Total queries: {len(test_queries)}")
    print(f"Cache hits: {cache_hits}")
    print(f"Cache hit rate: {cache_hit_rate:.1f}%")
    print(f"Average response time: {avg_time:.2f}s")
    print(f"Total time: {total_time:.2f}s")
    
    # Test performance endpoint
    try:
        perf_url = "http://localhost:5000/api/performance"
        perf_response = requests.get(perf_url, headers=headers)
        if perf_response.status_code == 200:
            perf_data = perf_response.json()
            print(f"\n📈 Server Performance Stats:")
            print(f"Total queries (server): {perf_data.get('total_queries', 0)}")
            print(f"Cache hits (server): {perf_data.get('cache_hits', 0)}")
            print(f"Cache hit rate (server): {perf_data.get('cache_hit_rate', '0%')}")
            print(f"Average response time (server): {perf_data.get('avg_response_time', '0s')}")
            print(f"Model loaded: {perf_data.get('model_loaded', False)}")
            print(f"Cache size: {perf_data.get('cache_size', 0)}")
    except Exception as e:
        print(f"❌ Could not fetch server stats: {e}")

def test_streaming_performance():
    """Test streaming endpoint performance"""
    url = "http://localhost:5000/api/query/stream"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token"
    }
    
    print(f"\n🌊 Testing Streaming Performance")
    print("=" * 40)
    
    query = "What is Article 370 of the Indian Constitution?"
    print(f"Query: {query}")
    
    start_time = time.time()
    try:
        response = requests.post(url, json={"query": query}, headers=headers, stream=True)
        
        if response.status_code == 200:
            print("Streaming response:")
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'response' in data:
                            print(f"Chunk: {data['response'][:50]}...")
                        if data.get('complete'):
                            break
                    except:
                        pass
            
            end_time = time.time()
            print(f"✅ Streaming completed in {end_time - start_time:.2f}s")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_lawgpt_performance()
    test_streaming_performance()
    print("\n✅ Performance testing complete!")
