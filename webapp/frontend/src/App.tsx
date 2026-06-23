import ScraperForm from './components/ScraperForm'
import LogViewer from './components/LogViewer'
import TutorialModal from './components/TutorialModal'

export default function App() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <ScraperForm />
      <LogViewer />
      <TutorialModal />
    </div>
  )
}
