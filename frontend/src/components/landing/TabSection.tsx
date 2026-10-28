"use client";
import { useState } from "react";
/* Structure and measurements preserved from the approved Optivio design. */
import { styles } from "./styles";
import { tabContent } from "./tab-content";

export function TabSection() {
  const [tab, setTab] = useState(0); const activeTab = tabContent[tab];
  return (
    <div className="framer-550ise" data-framer-name="Tab section" id="possibilidades">
      <div className="framer-11i66id" data-framer-name="Main-Container">
        <div className="framer-t699ib">
          <div className="framer-snskgj">
            <div className="framer-1rh1igh" data-framer-component-type="RichTextContainer" style={styles.s10}>
              <h2 className="framer-text framer-styles-preset-14gspjy" data-styles-preset="YemiXHrHL" dir="auto" style={styles.s53}>
                <span style={styles.s37}>
                  {"Engineered"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"for"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"every"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"stage"}
                </span>
                {" "}
                <span style={styles.s37}></span>
                {" "}
                <span style={styles.s37}>
                  {"of"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"search"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"growth"}
                </span>
              </h2>
            </div>
            <div className="framer-18n7tlq" data-framer-component-type="RichTextContainer" style={styles.s10}>
              <p className="framer-text framer-styles-preset-ygr40b" data-styles-preset="IISiIUjhp" dir="auto" style={styles.s54}>
                <span style={styles.s37}>
                  {"Optivio"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"isn’t"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"just"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"a"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"scanner—it’s"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"a"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"complete"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"intelligence"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"ecosystem."}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"Whether"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"you"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"are"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"identifying"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"technical"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"debt"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"or"}
                </span>
                {" "}
                <span style={styles.s37}></span>
                {" "}
                <span style={styles.s37}>
                  {"scaling"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"global"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"rankings,"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"our"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"clinical"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"tools"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"adapt"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"to"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"your"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"specific"}
                </span>
                {" "}
                <span style={styles.s37}>
                  {"workflow."}
                </span>
              </p>
            </div>
          </div>
          <div className="framer-z9cgv9-container" style={styles.s9} data-landing-appear="">
            <div className="ssr-variant hidden-v75cpf hidden-1825mw0">
              <section className="tabSecR17d7l6lp" style={styles.s103}>
                <style>{"\r\n.tabSecR17d7l6lp *:focus{outline:0;box-shadow:none}\r\n.tabSecR17d7l6lp *:focus-visible{outline:2px solid rgb(26, 26, 28);outline-offset:3px}\r\n.tabSecR17d7l6lp button{border:0;appearance:none;-webkit-appearance:none;margin:0;-webkit-tap-highlight-color:transparent}\r\n.tabSecR17d7l6lp button::-moz-focus-inner{border:0;padding:0}\r\n"}</style>
                <div role="tablist" style={styles.s104}>
                  <button type="button" role="tab" style={{...styles.s105, background: tab === 0 ? "rgb(249,247,226)" : "transparent"}} aria-selected={tab === 0} onClick={() => setTab(0)} tabIndex={tab === 0 ? 0 : -1} onKeyDown={event => { if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) { event.preventDefault(); const next = event.key === "Home" ? 0 : event.key === "End" ? 3 : (tab + (event.key === "ArrowRight" ? 1 : 3)) % 4; setTab(next); (event.currentTarget.parentElement?.children[next] as HTMLElement)?.focus(); } }}>
                    <span style={{...styles.s106, color: tab === 0 ? "rgb(26,26,28)" : "rgba(26,26,28,.45)"}}>
                      {"Planning"}
                    </span>
                  </button>
                  <button type="button" role="tab" style={{...styles.s105, background: tab === 1 ? "rgb(249,247,226)" : "transparent"}} aria-selected={tab === 1} onClick={() => setTab(1)} tabIndex={tab === 1 ? 0 : -1} onKeyDown={event => { if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) { event.preventDefault(); const next = event.key === "Home" ? 0 : event.key === "End" ? 3 : (tab + (event.key === "ArrowRight" ? 1 : 3)) % 4; setTab(next); (event.currentTarget.parentElement?.children[next] as HTMLElement)?.focus(); } }}>
                    <span style={{...styles.s107, color: tab === 1 ? "rgb(26,26,28)" : "rgba(26,26,28,.45)"}}>
                      {"SEO"}
                    </span>
                  </button>
                  <button type="button" role="tab" style={{...styles.s105, background: tab === 2 ? "rgb(249,247,226)" : "transparent"}} aria-selected={tab === 2} onClick={() => setTab(2)} tabIndex={tab === 2 ? 0 : -1} onKeyDown={event => { if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) { event.preventDefault(); const next = event.key === "Home" ? 0 : event.key === "End" ? 3 : (tab + (event.key === "ArrowRight" ? 1 : 3)) % 4; setTab(next); (event.currentTarget.parentElement?.children[next] as HTMLElement)?.focus(); } }}>
                    <span style={{...styles.s107, color: tab === 2 ? "rgb(26,26,28)" : "rgba(26,26,28,.45)"}}>
                      {"Marketing"}
                    </span>
                  </button>
                  <button type="button" role="tab" style={{...styles.s105, background: tab === 3 ? "rgb(249,247,226)" : "transparent"}} aria-selected={tab === 3} onClick={() => setTab(3)} tabIndex={tab === 3 ? 0 : -1} onKeyDown={event => { if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) { event.preventDefault(); const next = event.key === "Home" ? 0 : event.key === "End" ? 3 : (tab + (event.key === "ArrowRight" ? 1 : 3)) % 4; setTab(next); (event.currentTarget.parentElement?.children[next] as HTMLElement)?.focus(); } }}>
                    <span style={{...styles.s107, color: tab === 3 ? "rgb(26,26,28)" : "rgba(26,26,28,.45)"}}>
                      {"Keywords"}
                    </span>
                  </button>
                </div>
                <div style={styles.s108}>
                  <div style={styles.s109}>
                    <div style={styles.s110}>
                      <div style={styles.s111}>
                        <div style={styles.s112}>
                          <span style={styles.s113}>
                            {activeTab.label}
                          </span>
                          <div style={styles.s90}>
                            <h3 style={styles.s114}>
                              {activeTab.title}
                            </h3>
                            <p style={styles.s115}>
                              {activeTab.description}
                            </p>
                          </div>
                        </div>
                        <div style={styles.s116}>
                          <a className="framer-wlTbG framer-11q2sx framer-v-11q2sx framer-1pauw18" data-border="true" data-framer-name="Default" style={styles.s117}>
                            <div className="framer-dtf4ev" data-framer-name="Text Wrapper">
                              <div className="framer-1apu6do" data-framer-component-type="RichTextContainer" style={styles.s118}>
                                <p dir="auto" className="framer-text" style={styles.s4}>
                                  {activeTab.cta}
                                </p>
                              </div>
                              <div className="framer-5sx392" data-framer-component-type="RichTextContainer" style={styles.s119}>
                                <p dir="auto" className="framer-text" style={styles.s4}>
                                  {activeTab.cta}
                                </p>
                              </div>
                            </div>
                            <div className="framer-b6t5dl" style={styles.s120}>
                              <div className="framer-1942khh">
                                <div style={styles.s7} data-framer-background-image-wrapper="true">
                                  <img decoding="async" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                </div>
                              </div>
                              <div className="framer-251h4r">
                                <div style={styles.s7} data-framer-background-image-wrapper="true">
                                  <img decoding="async" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                </div>
                              </div>
                            </div>
                          </a>
                          <div style={styles.s121}>
                            <span style={styles.s122}>
                              {activeTab.number}
                            </span>
                            <span style={styles.s123}>
                              {activeTab.caption}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div style={styles.s124}>
                      <div style={{...styles.s125, backgroundImage: `url(${activeTab.image})`}}></div>
                    </div>
                  </div>
                </div>
              </section>
            </div>
            <div className="ssr-variant hidden-19vnmbx hidden-1825mw0 hidden-72rtr7">
              <section className="tabSecR1bd7l6lp" style={styles.s126}>
                <style>{"\r\n.tabSecR1bd7l6lp *:focus{outline:0;box-shadow:none}\r\n.tabSecR1bd7l6lp *:focus-visible{outline:2px solid rgb(26, 26, 28);outline-offset:3px}\r\n.tabSecR1bd7l6lp button{border:0;appearance:none;-webkit-appearance:none;margin:0;-webkit-tap-highlight-color:transparent}\r\n.tabSecR1bd7l6lp button::-moz-focus-inner{border:0;padding:0}\r\n"}</style>
                <div role="tablist" style={styles.s127}>
                  <button type="button" role="tab" style={{...styles.s105, background: tab === 0 ? "rgb(249,247,226)" : "transparent"}} aria-selected={tab === 0} onClick={() => setTab(0)} tabIndex={tab === 0 ? 0 : -1} onKeyDown={event => { if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) { event.preventDefault(); const next = event.key === "Home" ? 0 : event.key === "End" ? 3 : (tab + (event.key === "ArrowRight" ? 1 : 3)) % 4; setTab(next); (event.currentTarget.parentElement?.children[next] as HTMLElement)?.focus(); } }}>
                    <span style={{...styles.s128, color: tab === 0 ? "rgb(26,26,28)" : "rgba(26,26,28,.45)"}}>
                      {"Planning"}
                    </span>
                  </button>
                  <button type="button" role="tab" style={{...styles.s105, background: tab === 1 ? "rgb(249,247,226)" : "transparent"}} aria-selected={tab === 1} onClick={() => setTab(1)} tabIndex={tab === 1 ? 0 : -1} onKeyDown={event => { if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) { event.preventDefault(); const next = event.key === "Home" ? 0 : event.key === "End" ? 3 : (tab + (event.key === "ArrowRight" ? 1 : 3)) % 4; setTab(next); (event.currentTarget.parentElement?.children[next] as HTMLElement)?.focus(); } }}>
                    <span style={{...styles.s129, color: tab === 1 ? "rgb(26,26,28)" : "rgba(26,26,28,.45)"}}>
                      {"SEO"}
                    </span>
                  </button>
                  <button type="button" role="tab" style={{...styles.s105, background: tab === 2 ? "rgb(249,247,226)" : "transparent"}} aria-selected={tab === 2} onClick={() => setTab(2)} tabIndex={tab === 2 ? 0 : -1} onKeyDown={event => { if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) { event.preventDefault(); const next = event.key === "Home" ? 0 : event.key === "End" ? 3 : (tab + (event.key === "ArrowRight" ? 1 : 3)) % 4; setTab(next); (event.currentTarget.parentElement?.children[next] as HTMLElement)?.focus(); } }}>
                    <span style={{...styles.s129, color: tab === 2 ? "rgb(26,26,28)" : "rgba(26,26,28,.45)"}}>
                      {"Marketing"}
                    </span>
                  </button>
                  <button type="button" role="tab" style={{...styles.s105, background: tab === 3 ? "rgb(249,247,226)" : "transparent"}} aria-selected={tab === 3} onClick={() => setTab(3)} tabIndex={tab === 3 ? 0 : -1} onKeyDown={event => { if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) { event.preventDefault(); const next = event.key === "Home" ? 0 : event.key === "End" ? 3 : (tab + (event.key === "ArrowRight" ? 1 : 3)) % 4; setTab(next); (event.currentTarget.parentElement?.children[next] as HTMLElement)?.focus(); } }}>
                    <span style={{...styles.s129, color: tab === 3 ? "rgb(26,26,28)" : "rgba(26,26,28,.45)"}}>
                      {"Keywords"}
                    </span>
                  </button>
                </div>
                <div style={styles.s130}>
                  <div style={styles.s131}>
                    <div style={styles.s132}>
                      <div style={styles.s133}>
                        <div style={styles.s112}>
                          <span style={styles.s134}>
                            {activeTab.label}
                          </span>
                          <div style={styles.s90}>
                            <h3 style={styles.s135}>
                              {activeTab.title}
                            </h3>
                            <p style={styles.s115}>
                              {activeTab.description}
                            </p>
                          </div>
                        </div>
                        <div style={styles.s116}>
                          <a className="framer-wlTbG framer-11q2sx framer-v-11q2sx framer-1pauw18" data-border="true" data-framer-name="Default" style={styles.s117}>
                            <div className="framer-dtf4ev" data-framer-name="Text Wrapper">
                              <div className="framer-1apu6do" data-framer-component-type="RichTextContainer" style={styles.s118}>
                                <p dir="auto" className="framer-text" style={styles.s4}>
                                  {activeTab.cta}
                                </p>
                              </div>
                              <div className="framer-5sx392" data-framer-component-type="RichTextContainer" style={styles.s119}>
                                <p dir="auto" className="framer-text" style={styles.s4}>
                                  {activeTab.cta}
                                </p>
                              </div>
                            </div>
                            <div className="framer-b6t5dl" style={styles.s120}>
                              <div className="framer-1942khh">
                                <div style={styles.s7} data-framer-background-image-wrapper="true">
                                  <img decoding="async" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                </div>
                              </div>
                              <div className="framer-251h4r">
                                <div style={styles.s7} data-framer-background-image-wrapper="true">
                                  <img decoding="async" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                </div>
                              </div>
                            </div>
                          </a>
                          <div style={styles.s121}>
                            <span style={styles.s122}>
                              {activeTab.number}
                            </span>
                            <span style={styles.s123}>
                              {activeTab.caption}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div style={styles.s136}>
                      <div style={{...styles.s125, backgroundImage: `url(${activeTab.image})`}}></div>
                    </div>
                  </div>
                </div>
              </section>
            </div>
            <div className="ssr-variant hidden-v75cpf hidden-19vnmbx hidden-72rtr7">
              <section className="tabSecR1fd7l6lp" style={styles.s103}>
                <style>{"\r\n.tabSecR1fd7l6lp *:focus{outline:0;box-shadow:none}\r\n.tabSecR1fd7l6lp *:focus-visible{outline:2px solid rgb(26, 26, 28);outline-offset:3px}\r\n.tabSecR1fd7l6lp button{border:0;appearance:none;-webkit-appearance:none;margin:0;-webkit-tap-highlight-color:transparent}\r\n.tabSecR1fd7l6lp button::-moz-focus-inner{border:0;padding:0}\r\n"}</style>
                <div role="tablist" style={styles.s104}>
                  <button type="button" role="tab" style={{...styles.s105, background: tab === 0 ? "rgb(249,247,226)" : "transparent"}} aria-selected={tab === 0} onClick={() => setTab(0)} tabIndex={tab === 0 ? 0 : -1} onKeyDown={event => { if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) { event.preventDefault(); const next = event.key === "Home" ? 0 : event.key === "End" ? 3 : (tab + (event.key === "ArrowRight" ? 1 : 3)) % 4; setTab(next); (event.currentTarget.parentElement?.children[next] as HTMLElement)?.focus(); } }}>
                    <span style={{...styles.s106, color: tab === 0 ? "rgb(26,26,28)" : "rgba(26,26,28,.45)"}}>
                      {"Planning"}
                    </span>
                  </button>
                  <button type="button" role="tab" style={{...styles.s105, background: tab === 1 ? "rgb(249,247,226)" : "transparent"}} aria-selected={tab === 1} onClick={() => setTab(1)} tabIndex={tab === 1 ? 0 : -1} onKeyDown={event => { if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) { event.preventDefault(); const next = event.key === "Home" ? 0 : event.key === "End" ? 3 : (tab + (event.key === "ArrowRight" ? 1 : 3)) % 4; setTab(next); (event.currentTarget.parentElement?.children[next] as HTMLElement)?.focus(); } }}>
                    <span style={{...styles.s107, color: tab === 1 ? "rgb(26,26,28)" : "rgba(26,26,28,.45)"}}>
                      {"SEO"}
                    </span>
                  </button>
                  <button type="button" role="tab" style={{...styles.s105, background: tab === 2 ? "rgb(249,247,226)" : "transparent"}} aria-selected={tab === 2} onClick={() => setTab(2)} tabIndex={tab === 2 ? 0 : -1} onKeyDown={event => { if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) { event.preventDefault(); const next = event.key === "Home" ? 0 : event.key === "End" ? 3 : (tab + (event.key === "ArrowRight" ? 1 : 3)) % 4; setTab(next); (event.currentTarget.parentElement?.children[next] as HTMLElement)?.focus(); } }}>
                    <span style={{...styles.s107, color: tab === 2 ? "rgb(26,26,28)" : "rgba(26,26,28,.45)"}}>
                      {"Marketing"}
                    </span>
                  </button>
                  <button type="button" role="tab" style={{...styles.s105, background: tab === 3 ? "rgb(249,247,226)" : "transparent"}} aria-selected={tab === 3} onClick={() => setTab(3)} tabIndex={tab === 3 ? 0 : -1} onKeyDown={event => { if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) { event.preventDefault(); const next = event.key === "Home" ? 0 : event.key === "End" ? 3 : (tab + (event.key === "ArrowRight" ? 1 : 3)) % 4; setTab(next); (event.currentTarget.parentElement?.children[next] as HTMLElement)?.focus(); } }}>
                    <span style={{...styles.s107, color: tab === 3 ? "rgb(26,26,28)" : "rgba(26,26,28,.45)"}}>
                      {"Keywords"}
                    </span>
                  </button>
                </div>
                <div style={styles.s137}>
                  <div style={styles.s131}>
                    <div style={styles.s138}>
                      <div style={styles.s139}>
                        <div style={styles.s112}>
                          <span style={styles.s113}>
                            {activeTab.label}
                          </span>
                          <div style={styles.s90}>
                            <h3 style={styles.s114}>
                              {activeTab.title}
                            </h3>
                            <p style={styles.s115}>
                              {activeTab.description}
                            </p>
                          </div>
                        </div>
                        <div style={styles.s116}>
                          <a className="framer-wlTbG framer-11q2sx framer-v-11q2sx framer-1pauw18" data-border="true" data-framer-name="Default" style={styles.s117}>
                            <div className="framer-dtf4ev" data-framer-name="Text Wrapper">
                              <div className="framer-1apu6do" data-framer-component-type="RichTextContainer" style={styles.s118}>
                                <p dir="auto" className="framer-text" style={styles.s4}>
                                  {activeTab.cta}
                                </p>
                              </div>
                              <div className="framer-5sx392" data-framer-component-type="RichTextContainer" style={styles.s119}>
                                <p dir="auto" className="framer-text" style={styles.s4}>
                                  {activeTab.cta}
                                </p>
                              </div>
                            </div>
                            <div className="framer-b6t5dl" style={styles.s120}>
                              <div className="framer-1942khh">
                                <div style={styles.s7} data-framer-background-image-wrapper="true">
                                  <img decoding="async" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                </div>
                              </div>
                              <div className="framer-251h4r">
                                <div style={styles.s7} data-framer-background-image-wrapper="true">
                                  <img decoding="async" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                </div>
                              </div>
                            </div>
                          </a>
                          <div style={styles.s121}>
                            <span style={styles.s122}>
                              {activeTab.number}
                            </span>
                            <span style={styles.s123}>
                              {activeTab.caption}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div style={styles.s140}>
                      <div style={{...styles.s125, backgroundImage: `url(${activeTab.image})`}}></div>
                    </div>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
