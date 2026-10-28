"use client";
import { useState } from "react";
/* Structure and measurements preserved from the approved Optivio design. */
import { styles } from "./styles";

export function StepsSection() {
  const [step, setStep] = useState(0);
  return (
    <div className="framer-11zk8a6" data-framer-name="Steps section" id="como-funciona">
      <div className="framer-wcy77l" data-framer-name="Main-Container">
        <div className="framer-hmlrni">
          <div className="ssr-variant">
            <div className="framer-1j5jasd-container" style={styles.s9} data-landing-appear="">
              <div className="framer-DIxtH framer-4F4wF framer-smmrlk framer-v-smmrlk" data-border="true" data-framer-name="Variant 1" style={styles.s52}>
                <div className="framer-120864l" data-framer-component-type="RichTextContainer" style={styles.s34}>
                  <p className="framer-text framer-styles-preset-1s8g08" data-styles-preset="NxsGmJIB2" dir="auto" style={styles.s35}>
                    {"Princípios do produto"}
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div className="framer-1fkijrf">
            <div className="framer-1rhy9em" data-framer-component-type="RichTextContainer" style={styles.s10}>
              <h2 className="framer-text framer-styles-preset-14gspjy" data-styles-preset="YemiXHrHL" dir="auto" style={styles.s53}>
                <span style={styles.s37}>
                  {"Get"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"your"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"SEO"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"audit"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"in"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"3"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"Simple"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"Steps"}
                </span>
              </h2>
            </div>
            <div className="framer-1q69zlh" data-framer-component-type="RichTextContainer" style={styles.s10}>
              <p className="framer-text framer-styles-preset-1vz2vs0" data-styles-preset="lGB2bBCus" dir="auto" style={styles.s84}>
                <span style={styles.s37}>
                  {"From"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"deep-crawl"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"analysis"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"to"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"automated"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"optimization—Optivio"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"streamlines"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"your"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"entire"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"ranking"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"workflow"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"in"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"minutes."}
                </span>
              </p>
            </div>
          </div>
        </div>
        <div className="ssr-variant hidden-v75cpf">
          <div className="framer-102p4mu" style={styles.s9} data-landing-appear="">
            <div className="framer-6vc5vp-container">
              <div className="ssr-variant hidden-1825mw0">
                <div style={styles.s85}>
                  <div tabIndex={0} style={{...styles.s86, width: step === 0 ? 604 : 302, zIndex: step === 0 ? 2 : 1, transition: "width 600ms cubic-bezier(.22,1,.36,1)"}} role="button" aria-expanded={step === 0} onClick={() => setStep(0)} onMouseEnter={() => setStep(0)} onFocus={() => setStep(0)} onKeyDown={event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setStep(0); } }}>
                    <div style={styles.s87}>
                      <div style={styles.s88}>
                        <span style={styles.s89}>
                          {"01"}
                        </span>
                        <div style={styles.s90}>
                          <h3 style={styles.s70}>
                            {"Scan website"}
                          </h3>
                          <p style={styles.s91}>
                            {"Paste your URL and let our clinical engine run a comprehensive 360° technical scan instantly."}
                          </p>
                        </div>
                      </div>
                      <div style={styles.s92}>
                        <img src="/assets/landing/e756670efce9.jpg" alt="" decoding="async" style={styles.s93} />
                      </div>
                    </div>
                  </div>
                  <div tabIndex={0} style={{...styles.s94, width: step === 1 ? 604 : 302, zIndex: step === 1 ? 2 : 1, transition: "width 600ms cubic-bezier(.22,1,.36,1)"}} role="button" aria-expanded={step === 1} onClick={() => setStep(1)} onMouseEnter={() => setStep(1)} onFocus={() => setStep(1)} onKeyDown={event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setStep(1); } }}>
                    <div style={styles.s87}>
                      <div style={styles.s88}>
                        <span style={styles.s89}>
                          {"02"}
                        </span>
                        <div style={styles.s90}>
                          <h3 style={styles.s70}>
                            {"Get your audit report"}
                          </h3>
                          <p style={styles.s91}>
                            {"Access a high-fidelity breakdown of exactly what’s working, what’s broken, and what to fix first."}
                          </p>
                        </div>
                      </div>
                      <div style={styles.s92}>
                        <img src="/assets/landing/d004d446c75e.jpg" srcSet="/assets/landing/d004d446c75e.jpg 557w" alt="" decoding="async" style={styles.s93} sizes="(min-width: 1920px) 100vw, (min-width: 1440px) and (max-width: 1919.98px) 100vw, (min-width: 810px) and (max-width: 1439.98px) 100vw, (max-width: 809.98px) 100vw" />
                      </div>
                    </div>
                  </div>
                  <div tabIndex={0} style={{...styles.s94, width: step === 2 ? 604 : 302, zIndex: step === 2 ? 2 : 1, transition: "width 600ms cubic-bezier(.22,1,.36,1)"}} role="button" aria-expanded={step === 2} onClick={() => setStep(2)} onMouseEnter={() => setStep(2)} onFocus={() => setStep(2)} onKeyDown={event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setStep(2); } }}>
                    <div style={styles.s87}>
                      <div style={styles.s88}>
                        <span style={styles.s89}>
                          {"03"}
                        </span>
                        <div style={styles.s90}>
                          <h3 style={styles.s70}>
                            {"Optimize & Scale"}
                          </h3>
                          <p style={styles.s91}>
                            {"Use AI-driven tips to improve rankings and convert traffic into revenue automatically."}
                          </p>
                        </div>
                      </div>
                      <div style={styles.s92}>
                        <img src="/assets/landing/728269a0559d.jpg" srcSet="/assets/landing/728269a0559d.jpg 557w" alt="" decoding="async" style={styles.s93} sizes="(min-width: 1920px) 100vw, (min-width: 1440px) and (max-width: 1919.98px) 100vw, (min-width: 810px) and (max-width: 1439.98px) 100vw, (max-width: 809.98px) 100vw" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="ssr-variant hidden-19vnmbx hidden-72rtr7">
                <div style={styles.s95}>
                  <div style={styles.s96}>
                    <div style={styles.s97}>
                      <span style={styles.s89}>
                        {"01"}
                      </span>
                      <div style={styles.s90}>
                        <h3 style={styles.s98}>
                          {"Scan website"}
                        </h3>
                        <p style={styles.s91}>
                          {"Paste your URL and let our clinical engine run a comprehensive 360° technical scan instantly."}
                        </p>
                      </div>
                    </div>
                    <div style={styles.s99}>
                      <img src="/assets/landing/e756670efce9.jpg" alt="" decoding="async" style={styles.s93} />
                    </div>
                  </div>
                  <div style={styles.s96}>
                    <div style={styles.s97}>
                      <span style={styles.s89}>
                        {"02"}
                      </span>
                      <div style={styles.s90}>
                        <h3 style={styles.s98}>
                          {"Get your audit report"}
                        </h3>
                        <p style={styles.s91}>
                          {"Access a high-fidelity breakdown of exactly what’s working, what’s broken, and what to fix first."}
                        </p>
                      </div>
                    </div>
                    <div style={styles.s99}>
                      <img src="/assets/landing/d004d446c75e.jpg" srcSet="/assets/landing/d004d446c75e.jpg 557w" alt="" decoding="async" style={styles.s93} sizes="(min-width: 1920px) 100vw, (min-width: 1440px) and (max-width: 1919.98px) 100vw, (min-width: 810px) and (max-width: 1439.98px) 100vw, (max-width: 809.98px) 100vw" />
                    </div>
                  </div>
                  <div style={styles.s96}>
                    <div style={styles.s97}>
                      <span style={styles.s89}>
                        {"03"}
                      </span>
                      <div style={styles.s90}>
                        <h3 style={styles.s98}>
                          {"Optimize & Scale"}
                        </h3>
                        <p style={styles.s91}>
                          {"Use AI-driven tips to improve rankings and convert traffic into revenue automatically."}
                        </p>
                      </div>
                    </div>
                    <div style={styles.s99}>
                      <img src="/assets/landing/728269a0559d.jpg" srcSet="/assets/landing/728269a0559d.jpg 557w" alt="" decoding="async" style={styles.s93} sizes="(min-width: 1920px) 100vw, (min-width: 1440px) and (max-width: 1919.98px) 100vw, (min-width: 810px) and (max-width: 1439.98px) 100vw, (max-width: 809.98px) 100vw" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="ssr-variant hidden-19vnmbx hidden-1825mw0 hidden-72rtr7">
          <div className="framer-102p4mu" data-hide-scrollbars="true" style={styles.s9} data-landing-appear="">
            <div className="framer-6vc5vp-container">
              <div style={styles.s95}>
                <div style={styles.s100}>
                  <div style={styles.s101}>
                    <span style={styles.s89}>
                      {"01"}
                    </span>
                    <div style={styles.s90}>
                      <h3 style={styles.s98}>
                        {"Scan website"}
                      </h3>
                      <p style={styles.s91}>
                        {"Paste your URL and let our clinical engine run a comprehensive 360° technical scan instantly."}
                      </p>
                    </div>
                  </div>
                  <div style={styles.s102}>
                    <img src="/assets/landing/e756670efce9.jpg" alt="" decoding="async" style={styles.s93} />
                  </div>
                </div>
                <div style={styles.s100}>
                  <div style={styles.s101}>
                    <span style={styles.s89}>
                      {"02"}
                    </span>
                    <div style={styles.s90}>
                      <h3 style={styles.s98}>
                        {"Get your audit report"}
                      </h3>
                      <p style={styles.s91}>
                        {"Access a high-fidelity breakdown of exactly what’s working, what’s broken, and what to fix first."}
                      </p>
                    </div>
                  </div>
                  <div style={styles.s102}>
                    <img src="/assets/landing/d004d446c75e.jpg" srcSet="/assets/landing/d004d446c75e.jpg 557w" alt="" decoding="async" style={styles.s93} sizes="(min-width: 1920px) 100vw, (min-width: 1440px) and (max-width: 1919.98px) 100vw, (min-width: 810px) and (max-width: 1439.98px) 100vw, (max-width: 809.98px) 100vw" />
                  </div>
                </div>
                <div style={styles.s100}>
                  <div style={styles.s101}>
                    <span style={styles.s89}>
                      {"03"}
                    </span>
                    <div style={styles.s90}>
                      <h3 style={styles.s98}>
                        {"Optimize & Scale"}
                      </h3>
                      <p style={styles.s91}>
                        {"Use AI-driven tips to improve rankings and convert traffic into revenue automatically."}
                      </p>
                    </div>
                  </div>
                  <div style={styles.s102}>
                    <img src="/assets/landing/728269a0559d.jpg" srcSet="/assets/landing/728269a0559d.jpg 557w" alt="" decoding="async" style={styles.s93} sizes="(min-width: 1920px) 100vw, (min-width: 1440px) and (max-width: 1919.98px) 100vw, (min-width: 810px) and (max-width: 1439.98px) 100vw, (max-width: 809.98px) 100vw" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
