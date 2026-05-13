import { LayoutTemplate } from 'lucide-react';
import './Header.css';

export default function Header() {
  return (
    <header className="app-header glass-panel">
      <div className="container header-content">
        <div className="logo-section animate-float" style={{ animationDuration: '8s' }}>
          <div className="logo-icon-wrapper">
            <LayoutTemplate size={28} className="logo-icon" />
          </div>
          <h1 className="logo-text">
            doc<span className="text-gradient">Pipe</span>
          </h1>
        </div>
        <nav className="nav-links">
          <a href="#" className="nav-link">Documentation</a>
          <a href="https://github.com" target="_blank" rel="noreferrer" className="nav-link">GitHub</a>
        </nav>
      </div>
    </header>
  );
}
