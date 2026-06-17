function App() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <section className="mx-auto flex min-h-screen max-w-5xl flex-col items-center justify-center px-6 text-center">
        <p className="mb-3 text-sm font-semibold uppercase tracking-wide text-blue-600">
          Campus Course-Schedule Optimizer
        </p>

        <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-6xl">
          Build valid semester schedules faster.
        </h1>

        <p className="mb-8 max-w-2xl text-lg text-slate-600">
          A full-stack scheduling app that helps students generate course
          schedules based on prerequisites, class times, credit-hour goals, and
          personal preferences.
        </p>

        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-xl border bg-white p-5 shadow-sm">
            <h2 className="mb-2 font-semibold">Prerequisite Checks</h2>
            <p className="text-sm text-slate-600">
              Filters out courses the student is not eligible to take.
            </p>
          </div>

          <div className="rounded-xl border bg-white p-5 shadow-sm">
            <h2 className="mb-2 font-semibold">Conflict Detection</h2>
            <p className="text-sm text-slate-600">
              Rejects schedules with overlapping class times.
            </p>
          </div>

          <div className="rounded-xl border bg-white p-5 shadow-sm">
            <h2 className="mb-2 font-semibold">AI Planning Assistant</h2>
            <p className="text-sm text-slate-600">
              Uses Claude to convert natural-language preferences into structured
              scheduling constraints.
            </p>
          </div>
        </div>
      </section>
    </main>
  );
}

export default App;