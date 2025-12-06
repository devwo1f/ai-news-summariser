import React, { useState, useEffect, useRef, useCallback } from 'react';

// --- Components ---

const NewsCard = ({ article, innerRef }) => {
  return (
    <div 
      ref={innerRef}
      className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300 border border-gray-100 flex flex-col h-full animate-fade-in-up"
    >
      {article.image_url && (
        <img 
          src={article.image_url} 
          alt={article.title} 
          className="w-full h-48 object-cover"
          onError={(e) => e.target.style.display = 'none'} 
        />
      )}
      <div className="p-6 flex-1 flex flex-col">
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
          <span className="font-semibold text-blue-600">{article.source_name}</span>
          <span>•</span>
          <span>{new URL(article.url).hostname}</span>
        </div>
        
        <h3 className="text-xl font-bold text-gray-800 mb-3 leading-tight">
          <a href={article.url} target="_blank" rel="noopener noreferrer" className="hover:text-blue-600">
            {article.title}
          </a>
        </h3>

        {/* Real-time Summary Section */}
        {article.summary ? (
          <div className="bg-blue-50 p-4 rounded-lg mb-4 border-l-4 border-blue-500 transition-all duration-500">
            <p className="text-xs font-bold text-blue-500 uppercase mb-1">AI Summary</p>
            <p className="text-gray-700 text-sm leading-relaxed">{article.summary}</p>
          </div>
        ) : article.is_loading ? (
          <div className="bg-gray-50 p-4 rounded-lg mb-4 flex items-center space-x-3 border-l-4 border-gray-300">
            <div className="animate-spin h-4 w-4 border-2 border-blue-600 rounded-full border-t-transparent"></div>
            <p className="text-xs text-gray-500 font-medium">AI is reading article...</p>
          </div>
        ) : (
           <div className="bg-gray-50 p-4 rounded-lg mb-4">
             <p className="text-gray-400 text-sm italic truncate">
               {article.description || "Waiting for processing..."}
             </p>
           </div>
        )}

        <div className="mt-auto pt-4 flex justify-end">
          <a 
            href={article.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-700 transition-colors"
          >
            Read Original
            <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </a>
        </div>
      </div>
    </div>
  );
};

// --- Main App ---

function App() {
  const [query, setQuery] = useState('');
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false); 
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);
  
  // State for Infinite Scroll
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  
  const processedUrls = useRef(new Set());
  const observer = useRef();

  const categories = ["Technology", "Sports", "Business", "Health", "Science", "Entertainment"];

  // 0. Initial Load (Front Page Feed)
  useEffect(() => {
    // Load top headlines on startup
    fetchArticles("", 1, true);
    // eslint-disable-next-line
  }, []);

  // 1. Infinite Scroll Observer
  const lastArticleRef = useCallback(node => {
    if (loading || loadingMore) return;
    
    if (observer.current) observer.current.disconnect();
    
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        // Increment page and fetch more
        setPage(prevPage => {
            const nextPage = prevPage + 1;
            fetchArticles(query, nextPage, false);
            return nextPage;
        });
      }
    });
    
    if (node) observer.current.observe(node);
  }, [loading, loadingMore, hasMore, query]);

  // 2. Fetch Articles
  const fetchArticles = async (searchQuery, pageNum, isNewSearch = true) => {
    if (isNewSearch) {
        setLoading(true);
        setArticles([]); 
        processedUrls.current.clear();
        setHasMore(true);
        setPage(1); // Ensure page state matches
    } else {
        setLoadingMore(true);
    }

    setError(null);

    try {
      // Allow empty query for "Top Headlines"
      const url = `http://127.0.0.1:8000/news/search?q=${searchQuery}&page=${pageNum}`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.articles && data.articles.length > 0) {
        const initializedArticles = data.articles.map(art => ({ ...art, is_loading: true, summary: null }));
        
        if (isNewSearch) {
            setArticles(initializedArticles);
        } else {
            // Filter duplicates before adding
            setArticles(prev => {
                const newArts = initializedArticles.filter(
                    newArt => !prev.some(prevArt => prevArt.url === newArt.url)
                );
                return [...prev, ...newArts];
            });
        }
        
        summarizeAll(initializedArticles);
      } else {
        setHasMore(false); // Stop trying to load more
      }
    } catch (err) {
      console.error("Failed to fetch news:", err);
      setError("Failed to connect to the backend.");
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const summarizeAll = async (articlesList) => {
    for (const article of articlesList) {
      if (processedUrls.current.has(article.url)) continue;
      processedUrls.current.add(article.url);
      fetchSummary(article.url);
    }
  };

  const fetchSummary = async (url) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/news/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url })
      });
      const data = await response.json();

      setArticles(prevArticles => 
        prevArticles.map(art => 
          art.url === url 
            ? { ...art, summary: data.summary, is_loading: false } 
            : art
        )
      );
    } catch (err) {
      setArticles(prevArticles => 
        prevArticles.map(art => 
          art.url === url 
            ? { ...art, summary: "Failed to load summary.", is_loading: false } 
            : art
        )
      );
    }
  };

  const handleSearch = (e) => {
    e?.preventDefault();
    fetchArticles(query, 1, true);
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <nav className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <span className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                AI News<span className="text-gray-800">Brief</span>
              </span>
            </div>
            <div className="hidden md:flex space-x-8">
              <a href="#" className="text-gray-500 hover:text-gray-900">About</a>
              <a href="#" className="text-gray-500 hover:text-gray-900">Github</a>
            </div>
          </div>
        </div>
      </nav>

      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-16 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl mb-4">
            Brief News. <span className="text-blue-600">Infinite Feed.</span>
          </h1>
          <p className="text-xl text-gray-500 mb-8">
            Scroll down to see the world's top stories, summarized in real-time.
          </p>

          <form onSubmit={handleSearch} className="relative max-w-2xl mx-auto">
            <input
              type="text"
              className="w-full pl-6 pr-32 py-4 rounded-full border-2 border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all text-lg shadow-sm"
              placeholder="Search (or leave empty for Top Headlines)..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button 
              type="submit"
              disabled={loading}
              className="absolute right-2 top-2 bottom-2 px-6 bg-blue-600 text-white rounded-full font-medium hover:bg-blue-700 transition-colors disabled:bg-gray-400"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </form>

          <div className="mt-8 flex flex-wrap justify-center gap-2">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => {
                  setQuery(cat);
                  fetchArticles(cat, 1, true);
                }}
                className="px-4 py-2 rounded-full bg-gray-100 text-gray-600 text-sm font-medium hover:bg-gray-200 hover:text-gray-900 transition-colors"
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 pb-24">
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8 rounded-r text-red-700">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {articles.map((article, index) => {
                // Attach Ref to the LAST element only
                if (articles.length === index + 1) {
                    return <NewsCard innerRef={lastArticleRef} key={`${article.url}-${index}`} article={article} />
                } else {
                    return <NewsCard key={`${article.url}-${index}`} article={article} />
                }
            })}
        </div>

        {/* Loading States */}
        {loading && (
           <div className="text-center py-12">
               <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
               <p className="text-gray-500">Fetching headlines...</p>
           </div>
        )}
        
        {loadingMore && (
           <div className="text-center py-8 pb-12">
               <div className="inline-flex items-center px-4 py-2 bg-gray-100 rounded-full text-gray-500 text-sm">
                    <div className="animate-spin h-3 w-3 border-2 border-gray-500 rounded-full border-t-transparent mr-2"></div>
                    Loading more news...
               </div>
           </div>
        )}

        {!loading && !loadingMore && !hasMore && articles.length > 0 && (
           <div className="text-center py-12 text-gray-400">
               <p>You have reached the end of the news feed.</p>
           </div>
        )}
      </main>
    </div>
  );
}

export default App;