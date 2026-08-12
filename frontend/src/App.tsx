import { useState } from "react";

import {
  askNiyam,
  configureProfile,
  type Source,
} from "./api";

import "./App.css";

type AnswerBlock = {
  heading: string;
  bullets: string[];
};

function parseAnswer(answer: string): {
  intro: string;
  blocks: AnswerBlock[];
} {
  const lines = answer
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  if (lines.length === 0) {
    return {
      intro: "",
      blocks: [],
    };
  }

  const intro =
    lines[0].startsWith("- ") || lines[0].endsWith(":")
      ? ""
      : lines[0];

  const startIndex = intro ? 1 : 0;

  const blocks: AnswerBlock[] = [];

  let currentBlock: AnswerBlock | null = null;

  for (const line of lines.slice(startIndex)) {
    if (line.startsWith("- ")) {
      if (currentBlock) {
        currentBlock.bullets.push(
          line.substring(2).trim(),
        );
      }

      continue;
    }

    if (currentBlock) {
      blocks.push(currentBlock);
    }

    currentBlock = {
      heading: line.replace(/:$/, ""),
      bullets: [],
    };
  }

  if (currentBlock) {
    blocks.push(currentBlock);
  }

  return {
    intro,
    blocks,
  };
}

function App() {
  const [businessName, setBusinessName] =
    useState("");

  const [industry, setIndustry] =
    useState("");

  const [companySize, setCompanySize] =
    useState("");

  const [state, setState] =
    useState("");

  const [profileConfigured, setProfileConfigured] =
    useState(false);

  const [question, setQuestion] =
    useState("");

  const [answer, setAnswer] =
    useState("");

  const [sources, setSources] =
    useState<Source[]>([]);

  const [loadingProfile, setLoadingProfile] =
    useState(false);

  const [loadingQuestion, setLoadingQuestion] =
    useState(false);

  const [error, setError] =
    useState("");

  async function handleConfigureProfile() {
    if (
      !businessName.trim() ||
      !industry.trim() ||
      !companySize.trim() ||
      !state.trim()
    ) {
      return;
    }

    setLoadingProfile(true);
    setError("");

    try {
      await configureProfile({
        business_name: businessName,
        industry,
        company_size: companySize,
        state,
      });

      setProfileConfigured(true);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to configure business profile.",
      );
    } finally {
      setLoadingProfile(false);
    }
  }

  async function handleAsk() {
    if (!question.trim() || !profileConfigured) {
      return;
    }

    setLoadingQuestion(true);
    setError("");
    setAnswer("");
    setSources([]);

    try {
      const result = await askNiyam(question);

      setAnswer(result.answer);
      setSources(result.sources);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to contact Niyam.",
      );
    } finally {
      setLoadingQuestion(false);
    }
  }

  const parsedAnswer = answer
    ? parseAnswer(answer)
    : {
        intro: "",
        blocks: [],
      };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <div className="brand">
            PROJECT NIYAM
          </div>

          <div className="brand-subtitle">
            AI Compliance Officer
          </div>
        </div>

        <div className="status-indicator">
          <span className="status-dot" />

          {profileConfigured
            ? "Business configured"
            : "Setup required"}
        </div>
      </header>

      <main className="app-content">
        <section className="hero-section">
          <div className="hero-label">
            BUSINESS COMPLIANCE INTELLIGENCE
          </div>

          <h1>
            Ask Niyam about
            <br />
            your business.
          </h1>

          <p>
            Get answers grounded in your business
            documents, with source information attached
            to every answer.
          </p>
        </section>

        <section className="card">
          <div className="section-heading">
            <div>
              <span className="step-number">
                01
              </span>

              <h2>Business Profile</h2>
            </div>

            {profileConfigured && (
              <span className="configured-badge">
                Configured
              </span>
            )}
          </div>

          <p className="section-description">
            Tell Niyam which business it is assisting.
          </p>

          <div className="form-grid">
            <div className="form-field">
              <label htmlFor="business-name">
                Business name
              </label>

              <input
                id="business-name"
                value={businessName}
                onChange={(event) =>
                  setBusinessName(
                    event.target.value,
                  )
                }
                disabled={profileConfigured}
                placeholder="ABC Manufacturing Pvt Ltd"
              />
            </div>

            <div className="form-field">
              <label htmlFor="industry">
                Industry
              </label>

              <input
                id="industry"
                value={industry}
                onChange={(event) =>
                  setIndustry(
                    event.target.value,
                  )
                }
                disabled={profileConfigured}
                placeholder="Manufacturing"
              />
            </div>

            <div className="form-field">
              <label htmlFor="company-size">
                Company size
              </label>

              <input
                id="company-size"
                value={companySize}
                onChange={(event) =>
                  setCompanySize(
                    event.target.value,
                  )
                }
                disabled={profileConfigured}
                placeholder="Small"
              />
            </div>

            <div className="form-field">
              <label htmlFor="state">
                State
              </label>

              <input
                id="state"
                value={state}
                onChange={(event) =>
                  setState(
                    event.target.value,
                  )
                }
                disabled={profileConfigured}
                placeholder="Delhi"
              />
            </div>
          </div>

          {!profileConfigured && (
            <div className="card-actions">
              <button
                className="primary-button"
                onClick={handleConfigureProfile}
                disabled={
                  loadingProfile ||
                  !businessName.trim() ||
                  !industry.trim() ||
                  !companySize.trim() ||
                  !state.trim()
                }
              >
                {loadingProfile
                  ? "Configuring..."
                  : "Configure Business"}
              </button>
            </div>
          )}
        </section>

        <section className="card question-container">
          <div className="section-heading">
            <div>
              <span className="step-number">
                02
              </span>

              <h2>Ask Niyam</h2>
            </div>
          </div>

          <p className="section-description">
            Ask a question about your business documents.
          </p>

          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(
                event.target.value,
              )
            }
            placeholder={
              profileConfigured
                ? "Ask a question about your business documents..."
                : "Configure your business profile first..."
            }
            disabled={!profileConfigured}
            rows={5}
          />

          <div className="card-actions">
            <button
              className="primary-button"
              onClick={handleAsk}
              disabled={
                !profileConfigured ||
                loadingQuestion ||
                !question.trim()
              }
            >
              {loadingQuestion
                ? "Niyam is thinking..."
                : "Ask Niyam"}
            </button>
          </div>
        </section>

        {error && (
          <section className="card error-card">
            <strong>Something went wrong</strong>

            <p>{error}</p>
          </section>
        )}

        {answer && (
          <section className="answer-section">
            <div className="answer-header">
              <div>
                <span className="step-number">
                  03
                </span>

                <h2>Answer</h2>
              </div>
            </div>

            <div className="answer-content">
              {parsedAnswer.intro && (
                <p className="answer-intro">
                  {parsedAnswer.intro}
                </p>
              )}

              {parsedAnswer.blocks.map(
                (block, index) => (
                  <div
                    className="answer-block"
                    key={`${block.heading}-${index}`}
                  >
                    <h3>
                      {block.heading}
                    </h3>

                    {block.bullets.length > 0 && (
                      <ul>
                        {block.bullets.map(
                          (bullet, bulletIndex) => (
                            <li
                              key={`${bullet}-${bulletIndex}`}
                            >
                              {bullet}
                            </li>
                          ),
                        )}
                      </ul>
                    )}
                  </div>
                ),
              )}
            </div>
          </section>
        )}

        {sources.length > 0 && (
          <section className="sources-section">
            <div className="section-heading">
              <div>
                <span className="step-number">
                  04
                </span>

                <h2>Sources</h2>
              </div>
            </div>

            <div className="sources-list">
              {sources.map(
                (source, index) => (
                  <div
                    className="source"
                    key={`${source.document_id}-${source.page_number}-${index}`}
                  >
                    <strong>
                      {source.source}
                    </strong>

                    <span>
                      Page {source.page_number}
                    </span>
                  </div>
                ),
              )}
            </div>
          </section>
        )}
      </main>

      <footer className="app-footer">
        <span>
          Project Niyam v0.7.0
        </span>

        <span>
          Grounded AI Compliance
        </span>
      </footer>
    </div>
  );
}

export default App;