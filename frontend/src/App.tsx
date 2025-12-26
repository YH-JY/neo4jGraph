import './App.css';
import Toolbar from './components/Toolbar';
import Sidebar from './components/Sidebar';
import GraphCanvas from './components/GraphCanvas';
import DetailsPanel from './components/DetailsPanel';
import CypherConsole from './components/CypherConsole';

const App = () => {
  return (
    <div className="App">
      <Toolbar />
      <div className="layout">
        <Sidebar />
        <GraphCanvas />
        <DetailsPanel />
        <CypherConsole />
      </div>
    </div>
  );
};

export default App;
