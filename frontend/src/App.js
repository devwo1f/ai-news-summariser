import React, { useState } from 'react';

// --- Components ---

const NewsCard = ({ article }) => {
  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300 border border-gray-100">
      {article.image_url && (
        <img 
          src={article.image_url} 
          alt={article.title} 
          className="w-full h-48 object-cover"
          onError={(e) => e.target.style.display = 'none'} 
        />
      )}
      <div className="p-6">
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

        {/* AI Summary Section */}
        <div className="bg-blue-50 p-4 rounded-lg mb-4 border-l-4 border-blue-500">
          <p className="text-xs font-bold text-blue-500 uppercase mb-1">AI Summary</p>
          <p className="text-gray-700 text-sm leading-relaxed">
            {article.summary || "Generating summary..."}
          </p>
        </div>

        <div className="flex justify-between items-center mt-4">
           {/* Fallback description if no summary yet */}
          {!article.summary && (
             <p className="text-gray-400 text-xs truncate w-2/3">{article.description}</p>
          )}
          
          <a 
            href={article.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-700 transition-colors ml-auto"
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

const LoadingSpinner = () => (
  <div className="flex flex-col items-center justify-center py-12">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
    <p className="text-gray-500 animate-pulse">Reading articles & generating summaries...</p>
    <p className="text-xs text-gray-400 mt-2">(This uses a large AI model, please be patient!)</p>
  </div>
);

// --- Main App ---

function App() {
  const [query, setQuery] = useState('');
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const categories = ["Technology", "Sports", "Business", "Health", "Science", "Entertainment"];

  const searchNews = async (searchQuery) => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    setError(null);
    setArticles([]);

    try {
      // Connect to your FastAPI Backend
      const response = await fetch(`http://127.0.0.1:8000/news/search?q=${searchQuery}`);
      const data = await response.json();
      
      if (data.articles) {
        setArticles(data.articles);
      } else {
        setArticles([]);
      }
    } catch (err) {
      console.error("Failed to fetch news:", err);
      setError("Failed to connect to the backend. Is your Python server running?");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    searchNews(query);
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Navbar */}
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

      {/* Hero Search Section */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-16 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl mb-4">
            Brief News. <span className="text-blue-600">Zero Noise.</span>
          </h1>
          <p className="text-xl text-gray-500 mb-8">
            Get AI-generated summaries of the latest headlines in seconds.
          </p>

          <form onSubmit={handleSearch} className="relative max-w-2xl mx-auto">
            <input
              type="text"
              className="w-full pl-6 pr-32 py-4 rounded-full border-2 border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all text-lg shadow-sm"
              placeholder="Search for topics (e.g., 'FC Barcelona', 'Bitcoin')..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button 
              type="submit"
              disabled={loading}
              className="absolute right-2 top-2 bottom-2 px-6 bg-blue-600 text-white rounded-full font-medium hover:bg-blue-700 transition-colors disabled:bg-gray-400"
            >
              {loading ? 'Searching...' : 'Summarize'}
            </button>
          </form>

          {/* Categories */}
          <div className="mt-8 flex flex-wrap justify-center gap-2">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => {
                  setQuery(cat);
                  searchNews(cat);
                }}
                className="px-4 py-2 rounded-full bg-gray-100 text-gray-600 text-sm font-medium hover:bg-gray-200 hover:text-gray-900 transition-colors"
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content Feed */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8 rounded-r">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {loading ? (
          <LoadingSpinner />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {articles.map((article, index) => (
              <NewsCard key={index} article={article} />
            ))}
          </div>
        )}

        {!loading && articles.length === 0 && !error && (
          <div className="text-center text-gray-400 py-12">
            <p className="text-lg">No articles found. Try a search!</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;