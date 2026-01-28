import { Routes, Route } from 'react-router-dom';
import { useThemeStore } from './stores/themeStore';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import AnalyzePage from './pages/AnalyzePage';
import DashboardPage from './pages/DashboardPage';
import HistoryPage from './pages/HistoryPage';
import CallDetailPage from './pages/CallDetailPage';
import AdminPage from './pages/AdminPage';
import AIVoicePage from './pages/AIVoicePage';

function App() {
  const { isDark } = useThemeStore();

  return (
    <div className={isDark ? 'dark' : ''}>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/analyze" element={<AnalyzePage />} />
          <Route path="/ai-voice" element={<AIVoicePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/calls/:callId" element={<CallDetailPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </Layout>
    </div>
  );
}

export default App;
