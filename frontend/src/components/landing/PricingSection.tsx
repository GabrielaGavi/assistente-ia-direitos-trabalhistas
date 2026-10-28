"use client";
import { useState } from "react";
/* Structure and measurements preserved from the approved Optivio design. */
import { styles } from "./styles";
import { LandingPrice } from "./landing-price";

export function PricingSection() {
  const [yearly, setYearly] = useState(false);
  return (
    <div className="framer-i537n7" data-framer-name="Pricing section" id="acesso" data-yearly={yearly}>
      <div className="framer-17pok4g" data-framer-name="Main-Container">
        <div className="framer-t3wqtc">
          <div className="framer-1kbe167">
            <div className="ssr-variant">
              <div className="framer-1f1oam0-container" style={styles.s9} data-landing-appear="">
                <div className="framer-DIxtH framer-4F4wF framer-smmrlk framer-v-smmrlk" data-border="true" data-framer-name="Variant 1" style={styles.s153}>
                  <div className="framer-120864l" data-framer-component-type="RichTextContainer" style={styles.s34}>
                    <p className="framer-text framer-styles-preset-1s8g08" data-styles-preset="NxsGmJIB2" dir="auto" style={styles.s35}>
                      {"Acesso"}
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="framer-b9m210">
              <div className="framer-f5xtw7" data-framer-component-type="RichTextContainer" style={styles.s10}>
                <h2 className="framer-text framer-styles-preset-14gspjy" data-styles-preset="YemiXHrHL" dir="auto" style={styles.s53}>
                  <span style={styles.s37}>
                    {"Simple,"}
                  </span>
                  {" "}
                  <span style={styles.s37}>
                    {"transparent"}
                  </span>
                  {" "}
                  <span style={styles.s37}>
                    {"pricing"}
                  </span>
                </h2>
              </div>
              <div className="framer-1akef8w" data-framer-component-type="RichTextContainer" style={styles.s10}>
                <p className="framer-text framer-styles-preset-ygr40b" data-styles-preset="IISiIUjhp" dir="auto" style={styles.s54}>
                  <span style={styles.s37}>
                    {"Start"}
                  </span>
                  {" "}
                  <span style={styles.s37}>
                    {"for"}
                  </span>
                  {" "}
                  <span style={styles.s37}>
                    {"free"}
                  </span>
                  {" "}
                  <span style={styles.s37}>
                    {"and"}
                  </span>
                  {" "}
                  <span style={styles.s37}>
                    {"scale"}
                  </span>
                  {" "}
                  <span style={styles.s37}>
                    {"your"}
                  </span>
                  {" "}
                  <span style={styles.s37}>
                    {"organic"}
                  </span>
                  {" "}
                  <span style={styles.s37}>
                    {"growth"}
                  </span>
                  {" "}
                  <span style={styles.s37}>
                    {"as"}
                  </span>
                  {" "}
                  <span style={styles.s37}>
                    {"you"}
                  </span>
                  {" "}
                  <span style={styles.s37}>
                    {"expand."}
                  </span>
                  {" "}
                  <span style={styles.s37}>
                    {"No"}
                  </span>
                  {" "}
                  <span style={styles.s37}>
                    {"hidden"}
                  </span>
                  {" "}
                  <span style={styles.s37}>
                    {"fees."}
                  </span>
                </p>
              </div>
            </div>
          </div>
          <div className="framer-rqucin" style={styles.s9} data-landing-appear="">
            <div className="ssr-variant hidden-v75cpf hidden-1825mw0">
              <div className="framer-1k8kmco-container">
                <div className="framer-74M5h framer-1gju40r framer-v-1gju40r" data-framer-name="Variant 1" style={styles.s143}>
                  <div className="framer-1moefy3-container">
                    <div role="radiogroup" aria-label="Billing period" style={styles.s154}>
                      <div role="radio" tabIndex={0} style={{...styles.s155, background: !yearly ? "rgb(26,26,28)" : "transparent"}} aria-checked={!yearly} onClick={() => setYearly(false)} onKeyDown={event => { if (["Enter", " ", "ArrowLeft", "ArrowRight"].includes(event.key)) { event.preventDefault(); setYearly(value => !value); } }}>
                        <span style={{...styles.s156, color: !yearly ? "#fff" : "rgba(26,26,28,.6)"}}>
                          {"Monthly"}
                        </span>
                      </div>
                      <div role="radio" tabIndex={0} style={{...styles.s157, background: yearly ? "rgb(26,26,28)" : "transparent"}} aria-checked={yearly} onClick={() => setYearly(true)} onKeyDown={event => { if (["Enter", " ", "ArrowLeft", "ArrowRight"].includes(event.key)) { event.preventDefault(); setYearly(value => !value); } }}>
                        <span style={{...styles.s158, color: yearly ? "#fff" : "rgba(26,26,28,.6)"}}>
                          {"Yearly"}
                        </span>
                        <span style={{...styles.s159, color: yearly ? "#fff" : "rgba(26,26,28,.6)"}}>
                          {"Save 17%"}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="framer-29pxex" data-framer-name="Cards">
                    <div className="framer-a7y0yj-container">
                      <div className="framer-hydXV framer-vUdMM framer-1w91lyh framer-v-1w91lyh" data-framer-name="Variant 1" style={styles.s160}>
                        <div className="framer-1e3dy5k" style={styles.s161}>
                          <div className="framer-16e2h5o">
                            <div className="framer-44bnwe" data-border="true" style={styles.s162}>
                              <div className="framer-11rz544">
                                <div className="framer-1f9oqu1" data-framer-component-type="RichTextContainer" style={styles.s163}>
                                  <h6 className="framer-text framer-styles-preset-42t0hg" data-styles-preset="vCV2RaSbZ" dir="auto" style={styles.s164}>
                                    {"Free"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-11h22j1">
                                <LandingPrice monthly="00" yearly="00" annual={yearly} />
                                <div className="framer-1a8vhk8" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"For personal blogs and  initial testing."}
                                  </h6>
                                </div>
                              </div>
                            </div>
                            <div className="framer-i87gq4">
                              <div className="framer-1evplsw">
                                <svg className="framer-TLxVQ framer-lawvxb" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-90si9u" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"1 Website Project"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-8j5rwf">
                                <svg className="framer-TLxVQ framer-ojm0ar" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-llbg3p" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Weekly Clinical Audit"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-jrv0q8">
                                <svg className="framer-TLxVQ framer-xsibkc" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-9sgpuz" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"100 Page Crawl Limit"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5c02c7">
                                <svg className="framer-TLxVQ framer-1bfeby9" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1a8uimd" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Basic Keyword Tracking"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5yzw1p">
                                <svg className="framer-TLxVQ framer-1v70mff" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-hca7rq" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Optivio Branded Reports"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-iabj9q">
                                <svg className="framer-TLxVQ framer-fe52zd" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1ikx8v4" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Optivio branded dashboard"}
                                  </h6>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div className="framer-15noqg-container">
                            <a className="framer-wlTbG framer-11q2sx framer-v-11q2sx framer-1pauw18" data-border="true" data-framer-name="Default" href="/chat" style={styles.s168}>
                              <div className="framer-dtf4ev" data-framer-name="Text Wrapper">
                                <div className="framer-1apu6do" data-framer-component-type="RichTextContainer" style={styles.s3}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Experimentar"}
                                  </p>
                                </div>
                                <div className="framer-5sx392" data-framer-component-type="RichTextContainer" style={styles.s5}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Experimentar"}
                                  </p>
                                </div>
                              </div>
                              <div className="framer-b6t5dl" style={styles.s6}>
                                <div className="framer-1942khh">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                                <div className="framer-251h4r">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                              </div>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="framer-vy6e72-container">
                      <div className="framer-hydXV framer-vUdMM framer-1w91lyh framer-v-1w91lyh" data-framer-name="Variant 1" style={styles.s160}>
                        <div className="framer-1e3dy5k" style={styles.s161}>
                          <div className="framer-16e2h5o">
                            <div className="framer-44bnwe" data-border="true" style={styles.s162}>
                              <div className="framer-11rz544">
                                <div className="framer-1f9oqu1" data-framer-component-type="RichTextContainer" style={styles.s163}>
                                  <h6 className="framer-text framer-styles-preset-42t0hg" data-styles-preset="vCV2RaSbZ" dir="auto" style={styles.s164}>
                                    {"Starter"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-11h22j1">
                                <LandingPrice monthly="29" yearly="99" annual={yearly} />
                                <div className="framer-1a8vhk8" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"For growing startups and  small sites."}
                                  </h6>
                                </div>
                              </div>
                            </div>
                            <div className="framer-i87gq4">
                              <div className="framer-1evplsw">
                                <svg className="framer-TLxVQ framer-lawvxb" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-90si9u" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"3 Website Projects"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-8j5rwf">
                                <svg className="framer-TLxVQ framer-ojm0ar" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-llbg3p" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Daily Clinical Audits"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-jrv0q8">
                                <svg className="framer-TLxVQ framer-xsibkc" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-9sgpuz" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"1,000 Page Crawl Limit"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5c02c7">
                                <svg className="framer-TLxVQ framer-1bfeby9" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1a8uimd" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Competitor Gap Analysis"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5yzw1p">
                                <svg className="framer-TLxVQ framer-1v70mff" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-hca7rq" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Remove Optivio Branding"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-iabj9q">
                                <svg className="framer-TLxVQ framer-fe52zd" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1ikx8v4" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Unlimited Projects"}
                                  </h6>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div className="framer-15noqg-container">
                            <a className="framer-wlTbG framer-11q2sx framer-v-11q2sx framer-1pauw18" data-border="true" data-framer-name="Default" href="/chat" style={styles.s168}>
                              <div className="framer-dtf4ev" data-framer-name="Text Wrapper">
                                <div className="framer-1apu6do" data-framer-component-type="RichTextContainer" style={styles.s3}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                                <div className="framer-5sx392" data-framer-component-type="RichTextContainer" style={styles.s5}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                              </div>
                              <div className="framer-b6t5dl" style={styles.s6}>
                                <div className="framer-1942khh">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                                <div className="framer-251h4r">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                              </div>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="framer-lydd2k-container">
                      <div className="framer-hydXV framer-vUdMM framer-1w91lyh framer-v-o8vmhi" data-framer-name="Variant 2" style={styles.s169}>
                        <div className="framer-1e3dy5k" style={styles.s170}>
                          <div className="framer-16e2h5o">
                            <div className="framer-44bnwe" data-border="true" style={styles.s162}>
                              <div className="framer-11rz544">
                                <div className="framer-1f9oqu1" data-framer-component-type="RichTextContainer" style={styles.s163}>
                                  <h6 className="framer-text framer-styles-preset-42t0hg" data-styles-preset="vCV2RaSbZ" dir="auto" style={styles.s164}>
                                    {"Plus"}
                                  </h6>
                                </div>
                                <div className="framer-o3wtx6-container">
                                  <div className="framer-DIxtH framer-4F4wF framer-smmrlk framer-v-smmrlk" data-border="true" data-framer-name="Variant 1" style={styles.s171}>
                                    <div className="framer-120864l" data-framer-component-type="RichTextContainer" style={styles.s34}>
                                      <p className="framer-text framer-styles-preset-1s8g08" data-styles-preset="NxsGmJIB2" dir="auto" style={styles.s35}>
                                        {"Most popular"}
                                      </p>
                                    </div>
                                  </div>
                                </div>
                              </div>
                              <div className="framer-11h22j1">
                                <LandingPrice monthly="199" yearly="399" annual={yearly} />
                                <div className="framer-1a8vhk8" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Most Popular. For scaling  businesses."}
                                  </h6>
                                </div>
                              </div>
                            </div>
                            <div className="framer-i87gq4">
                              <div className="framer-1evplsw">
                                <svg className="framer-TLxVQ framer-lawvxb" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-90si9u" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Unlimited Projects"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-8j5rwf">
                                <svg className="framer-TLxVQ framer-ojm0ar" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-llbg3p" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Real-time Site Monitoring"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-jrv0q8">
                                <svg className="framer-TLxVQ framer-xsibkc" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-9sgpuz" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"10,000 Page Crawl Limit"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5c02c7">
                                <svg className="framer-TLxVQ framer-1bfeby9" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1a8uimd" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Full API & Webhook Access"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5yzw1p">
                                <svg className="framer-TLxVQ framer-1v70mff" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-hca7rq" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Priority Developer Support"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-iabj9q">
                                <svg className="framer-TLxVQ framer-fe52zd" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1ikx8v4" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Advanced Security & SSO"}
                                  </h6>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div className="framer-15noqg-container">
                            <a className="framer-wlTbG framer-11q2sx framer-v-11q2sx framer-1pauw18" data-border="true" data-framer-name="Default" href="/chat" style={styles.s172}>
                              <div className="framer-dtf4ev" data-framer-name="Text Wrapper">
                                <div className="framer-1apu6do" data-framer-component-type="RichTextContainer" style={styles.s3}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                                <div className="framer-5sx392" data-framer-component-type="RichTextContainer" style={styles.s5}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                              </div>
                              <div className="framer-b6t5dl" style={styles.s6}>
                                <div className="framer-1942khh">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                                <div className="framer-251h4r">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                              </div>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="framer-5p41s1-container">
                      <div className="framer-hydXV framer-vUdMM framer-1w91lyh framer-v-1w91lyh" data-framer-name="Variant 1" style={styles.s160}>
                        <div className="framer-1e3dy5k" style={styles.s161}>
                          <div className="framer-16e2h5o">
                            <div className="framer-44bnwe" data-border="true" style={styles.s162}>
                              <div className="framer-11rz544">
                                <div className="framer-1f9oqu1" data-framer-component-type="RichTextContainer" style={styles.s163}>
                                  <h6 className="framer-text framer-styles-preset-42t0hg" data-styles-preset="vCV2RaSbZ" dir="auto" style={styles.s164}>
                                    {"Enterprise"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-11h22j1">
                                <LandingPrice monthly="499" yearly="899" annual={yearly} />
                                <div className="framer-1a8vhk8" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"For agencies requiring high- volume infra."}
                                  </h6>
                                </div>
                              </div>
                            </div>
                            <div className="framer-i87gq4">
                              <div className="framer-1evplsw">
                                <svg className="framer-TLxVQ framer-lawvxb" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-90si9u" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Custom Crawl Limits"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-8j5rwf">
                                <svg className="framer-TLxVQ framer-ojm0ar" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-llbg3p" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Dedicated SEO Strategist"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-jrv0q8">
                                <svg className="framer-TLxVQ framer-xsibkc" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-9sgpuz" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Advanced Security & SSO"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5c02c7">
                                <svg className="framer-TLxVQ framer-1bfeby9" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1a8uimd" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Custom Contract & Billing"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5yzw1p">
                                <svg className="framer-TLxVQ framer-1v70mff" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-hca7rq" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Competitor Gap Analysis"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-iabj9q">
                                <svg className="framer-TLxVQ framer-fe52zd" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1ikx8v4" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Daily Clinical Audits"}
                                  </h6>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div className="framer-15noqg-container">
                            <a className="framer-wlTbG framer-11q2sx framer-v-11q2sx framer-1pauw18" data-border="true" data-framer-name="Default" href="/chat" style={styles.s168}>
                              <div className="framer-dtf4ev" data-framer-name="Text Wrapper">
                                <div className="framer-1apu6do" data-framer-component-type="RichTextContainer" style={styles.s3}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                                <div className="framer-5sx392" data-framer-component-type="RichTextContainer" style={styles.s5}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                              </div>
                              <div className="framer-b6t5dl" style={styles.s6}>
                                <div className="framer-1942khh">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                                <div className="framer-251h4r">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                              </div>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="ssr-variant hidden-19vnmbx hidden-1825mw0 hidden-72rtr7">
              <div className="framer-1k8kmco-container">
                <div className="framer-74M5h framer-1gju40r framer-v-sr6mo4" data-framer-name="Phone" style={styles.s143}>
                  <div className="framer-1moefy3-container">
                    <div role="radiogroup" aria-label="Billing period" style={styles.s154}>
                      <div role="radio" tabIndex={0} style={{...styles.s155, background: !yearly ? "rgb(26,26,28)" : "transparent"}} aria-checked={!yearly} onClick={() => setYearly(false)} onKeyDown={event => { if (["Enter", " ", "ArrowLeft", "ArrowRight"].includes(event.key)) { event.preventDefault(); setYearly(value => !value); } }}>
                        <span style={{...styles.s156, color: !yearly ? "#fff" : "rgba(26,26,28,.6)"}}>
                          {"Monthly"}
                        </span>
                      </div>
                      <div role="radio" tabIndex={0} style={{...styles.s157, background: yearly ? "rgb(26,26,28)" : "transparent"}} aria-checked={yearly} onClick={() => setYearly(true)} onKeyDown={event => { if (["Enter", " ", "ArrowLeft", "ArrowRight"].includes(event.key)) { event.preventDefault(); setYearly(value => !value); } }}>
                        <span style={{...styles.s158, color: yearly ? "#fff" : "rgba(26,26,28,.6)"}}>
                          {"Yearly"}
                        </span>
                        <span style={{...styles.s159, color: yearly ? "#fff" : "rgba(26,26,28,.6)"}}>
                          {"Save 17%"}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="framer-29pxex" data-framer-name="Cards">
                    <div className="framer-a7y0yj-container">
                      <div className="framer-hydXV framer-vUdMM framer-1w91lyh framer-v-1w91lyh" data-framer-name="Variant 1" style={styles.s160}>
                        <div className="framer-1e3dy5k" style={styles.s161}>
                          <div className="framer-16e2h5o">
                            <div className="framer-44bnwe" data-border="true" style={styles.s162}>
                              <div className="framer-11rz544">
                                <div className="framer-1f9oqu1" data-framer-component-type="RichTextContainer" style={styles.s163}>
                                  <h6 className="framer-text framer-styles-preset-42t0hg" data-styles-preset="vCV2RaSbZ" dir="auto" style={styles.s164}>
                                    {"Free"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-11h22j1">
                                <LandingPrice monthly="00" yearly="00" annual={yearly} />
                                <div className="framer-1a8vhk8" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"For personal blogs and  initial testing."}
                                  </h6>
                                </div>
                              </div>
                            </div>
                            <div className="framer-i87gq4">
                              <div className="framer-1evplsw">
                                <svg className="framer-TLxVQ framer-lawvxb" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-90si9u" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"1 Website Project"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-8j5rwf">
                                <svg className="framer-TLxVQ framer-ojm0ar" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-llbg3p" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Weekly Clinical Audit"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-jrv0q8">
                                <svg className="framer-TLxVQ framer-xsibkc" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-9sgpuz" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"100 Page Crawl Limit"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5c02c7">
                                <svg className="framer-TLxVQ framer-1bfeby9" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1a8uimd" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Basic Keyword Tracking"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5yzw1p">
                                <svg className="framer-TLxVQ framer-1v70mff" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-hca7rq" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Optivio Branded Reports"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-iabj9q">
                                <svg className="framer-TLxVQ framer-fe52zd" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1ikx8v4" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Optivio branded dashboard"}
                                  </h6>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div className="framer-15noqg-container">
                            <a className="framer-wlTbG framer-11q2sx framer-v-11q2sx framer-1pauw18" data-border="true" data-framer-name="Default" href="/chat" style={styles.s168}>
                              <div className="framer-dtf4ev" data-framer-name="Text Wrapper">
                                <div className="framer-1apu6do" data-framer-component-type="RichTextContainer" style={styles.s3}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Experimentar"}
                                  </p>
                                </div>
                                <div className="framer-5sx392" data-framer-component-type="RichTextContainer" style={styles.s5}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Experimentar"}
                                  </p>
                                </div>
                              </div>
                              <div className="framer-b6t5dl" style={styles.s6}>
                                <div className="framer-1942khh">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                                <div className="framer-251h4r">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                              </div>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="framer-vy6e72-container">
                      <div className="framer-hydXV framer-vUdMM framer-1w91lyh framer-v-1w91lyh" data-framer-name="Variant 1" style={styles.s160}>
                        <div className="framer-1e3dy5k" style={styles.s161}>
                          <div className="framer-16e2h5o">
                            <div className="framer-44bnwe" data-border="true" style={styles.s162}>
                              <div className="framer-11rz544">
                                <div className="framer-1f9oqu1" data-framer-component-type="RichTextContainer" style={styles.s163}>
                                  <h6 className="framer-text framer-styles-preset-42t0hg" data-styles-preset="vCV2RaSbZ" dir="auto" style={styles.s164}>
                                    {"Starter"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-11h22j1">
                                <LandingPrice monthly="29" yearly="99" annual={yearly} />
                                <div className="framer-1a8vhk8" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"For growing startups and  small sites."}
                                  </h6>
                                </div>
                              </div>
                            </div>
                            <div className="framer-i87gq4">
                              <div className="framer-1evplsw">
                                <svg className="framer-TLxVQ framer-lawvxb" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-90si9u" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"3 Website Projects"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-8j5rwf">
                                <svg className="framer-TLxVQ framer-ojm0ar" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-llbg3p" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Daily Clinical Audits"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-jrv0q8">
                                <svg className="framer-TLxVQ framer-xsibkc" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-9sgpuz" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"1,000 Page Crawl Limit"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5c02c7">
                                <svg className="framer-TLxVQ framer-1bfeby9" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1a8uimd" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Competitor Gap Analysis"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5yzw1p">
                                <svg className="framer-TLxVQ framer-1v70mff" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-hca7rq" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Remove Optivio Branding"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-iabj9q">
                                <svg className="framer-TLxVQ framer-fe52zd" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1ikx8v4" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Unlimited Projects"}
                                  </h6>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div className="framer-15noqg-container">
                            <a className="framer-wlTbG framer-11q2sx framer-v-11q2sx framer-1pauw18" data-border="true" data-framer-name="Default" href="/chat" style={styles.s168}>
                              <div className="framer-dtf4ev" data-framer-name="Text Wrapper">
                                <div className="framer-1apu6do" data-framer-component-type="RichTextContainer" style={styles.s3}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                                <div className="framer-5sx392" data-framer-component-type="RichTextContainer" style={styles.s5}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                              </div>
                              <div className="framer-b6t5dl" style={styles.s6}>
                                <div className="framer-1942khh">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                                <div className="framer-251h4r">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                              </div>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="framer-lydd2k-container">
                      <div className="framer-hydXV framer-vUdMM framer-1w91lyh framer-v-o8vmhi" data-framer-name="Variant 2" style={styles.s169}>
                        <div className="framer-1e3dy5k" style={styles.s170}>
                          <div className="framer-16e2h5o">
                            <div className="framer-44bnwe" data-border="true" style={styles.s162}>
                              <div className="framer-11rz544">
                                <div className="framer-1f9oqu1" data-framer-component-type="RichTextContainer" style={styles.s163}>
                                  <h6 className="framer-text framer-styles-preset-42t0hg" data-styles-preset="vCV2RaSbZ" dir="auto" style={styles.s164}>
                                    {"Plus"}
                                  </h6>
                                </div>
                                <div className="framer-o3wtx6-container">
                                  <div className="framer-DIxtH framer-4F4wF framer-smmrlk framer-v-smmrlk" data-border="true" data-framer-name="Variant 1" style={styles.s171}>
                                    <div className="framer-120864l" data-framer-component-type="RichTextContainer" style={styles.s34}>
                                      <p className="framer-text framer-styles-preset-1s8g08" data-styles-preset="NxsGmJIB2" dir="auto" style={styles.s35}>
                                        {"Most popular"}
                                      </p>
                                    </div>
                                  </div>
                                </div>
                              </div>
                              <div className="framer-11h22j1">
                                <LandingPrice monthly="199" yearly="399" annual={yearly} />
                                <div className="framer-1a8vhk8" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Most Popular. For scaling  businesses."}
                                  </h6>
                                </div>
                              </div>
                            </div>
                            <div className="framer-i87gq4">
                              <div className="framer-1evplsw">
                                <svg className="framer-TLxVQ framer-lawvxb" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-90si9u" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Unlimited Projects"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-8j5rwf">
                                <svg className="framer-TLxVQ framer-ojm0ar" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-llbg3p" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Real-time Site Monitoring"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-jrv0q8">
                                <svg className="framer-TLxVQ framer-xsibkc" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-9sgpuz" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"10,000 Page Crawl Limit"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5c02c7">
                                <svg className="framer-TLxVQ framer-1bfeby9" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1a8uimd" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Full API & Webhook Access"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5yzw1p">
                                <svg className="framer-TLxVQ framer-1v70mff" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-hca7rq" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Priority Developer Support"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-iabj9q">
                                <svg className="framer-TLxVQ framer-fe52zd" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1ikx8v4" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Advanced Security & SSO"}
                                  </h6>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div className="framer-15noqg-container">
                            <a className="framer-wlTbG framer-11q2sx framer-v-11q2sx framer-1pauw18" data-border="true" data-framer-name="Default" href="/chat" style={styles.s172}>
                              <div className="framer-dtf4ev" data-framer-name="Text Wrapper">
                                <div className="framer-1apu6do" data-framer-component-type="RichTextContainer" style={styles.s3}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                                <div className="framer-5sx392" data-framer-component-type="RichTextContainer" style={styles.s5}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                              </div>
                              <div className="framer-b6t5dl" style={styles.s6}>
                                <div className="framer-1942khh">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                                <div className="framer-251h4r">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                              </div>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="framer-5p41s1-container">
                      <div className="framer-hydXV framer-vUdMM framer-1w91lyh framer-v-1w91lyh" data-framer-name="Variant 1" style={styles.s160}>
                        <div className="framer-1e3dy5k" style={styles.s161}>
                          <div className="framer-16e2h5o">
                            <div className="framer-44bnwe" data-border="true" style={styles.s162}>
                              <div className="framer-11rz544">
                                <div className="framer-1f9oqu1" data-framer-component-type="RichTextContainer" style={styles.s163}>
                                  <h6 className="framer-text framer-styles-preset-42t0hg" data-styles-preset="vCV2RaSbZ" dir="auto" style={styles.s164}>
                                    {"Enterprise"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-11h22j1">
                                <LandingPrice monthly="499" yearly="899" annual={yearly} />
                                <div className="framer-1a8vhk8" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"For agencies requiring high- volume infra."}
                                  </h6>
                                </div>
                              </div>
                            </div>
                            <div className="framer-i87gq4">
                              <div className="framer-1evplsw">
                                <svg className="framer-TLxVQ framer-lawvxb" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-90si9u" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Custom Crawl Limits"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-8j5rwf">
                                <svg className="framer-TLxVQ framer-ojm0ar" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-llbg3p" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Dedicated SEO Strategist"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-jrv0q8">
                                <svg className="framer-TLxVQ framer-xsibkc" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-9sgpuz" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Advanced Security & SSO"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5c02c7">
                                <svg className="framer-TLxVQ framer-1bfeby9" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1a8uimd" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Custom Contract & Billing"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5yzw1p">
                                <svg className="framer-TLxVQ framer-1v70mff" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-hca7rq" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Competitor Gap Analysis"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-iabj9q">
                                <svg className="framer-TLxVQ framer-fe52zd" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1ikx8v4" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Daily Clinical Audits"}
                                  </h6>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div className="framer-15noqg-container">
                            <a className="framer-wlTbG framer-11q2sx framer-v-11q2sx framer-1pauw18" data-border="true" data-framer-name="Default" href="/chat" style={styles.s168}>
                              <div className="framer-dtf4ev" data-framer-name="Text Wrapper">
                                <div className="framer-1apu6do" data-framer-component-type="RichTextContainer" style={styles.s3}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                                <div className="framer-5sx392" data-framer-component-type="RichTextContainer" style={styles.s5}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                              </div>
                              <div className="framer-b6t5dl" style={styles.s6}>
                                <div className="framer-1942khh">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                                <div className="framer-251h4r">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                              </div>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="ssr-variant hidden-v75cpf hidden-19vnmbx hidden-72rtr7">
              <div className="framer-1k8kmco-container">
                <div className="framer-74M5h framer-1gju40r framer-v-1twwqhx" data-framer-name="Tablet" style={styles.s143}>
                  <div className="framer-1moefy3-container">
                    <div role="radiogroup" aria-label="Billing period" style={styles.s154}>
                      <div role="radio" tabIndex={0} style={{...styles.s155, background: !yearly ? "rgb(26,26,28)" : "transparent"}} aria-checked={!yearly} onClick={() => setYearly(false)} onKeyDown={event => { if (["Enter", " ", "ArrowLeft", "ArrowRight"].includes(event.key)) { event.preventDefault(); setYearly(value => !value); } }}>
                        <span style={{...styles.s156, color: !yearly ? "#fff" : "rgba(26,26,28,.6)"}}>
                          {"Monthly"}
                        </span>
                      </div>
                      <div role="radio" tabIndex={0} style={{...styles.s157, background: yearly ? "rgb(26,26,28)" : "transparent"}} aria-checked={yearly} onClick={() => setYearly(true)} onKeyDown={event => { if (["Enter", " ", "ArrowLeft", "ArrowRight"].includes(event.key)) { event.preventDefault(); setYearly(value => !value); } }}>
                        <span style={{...styles.s158, color: yearly ? "#fff" : "rgba(26,26,28,.6)"}}>
                          {"Yearly"}
                        </span>
                        <span style={{...styles.s159, color: yearly ? "#fff" : "rgba(26,26,28,.6)"}}>
                          {"Save 17%"}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="framer-29pxex" data-framer-name="Cards">
                    <div className="framer-a7y0yj-container">
                      <div className="framer-hydXV framer-vUdMM framer-1w91lyh framer-v-1w91lyh" data-framer-name="Variant 1" style={styles.s160}>
                        <div className="framer-1e3dy5k" style={styles.s161}>
                          <div className="framer-16e2h5o">
                            <div className="framer-44bnwe" data-border="true" style={styles.s162}>
                              <div className="framer-11rz544">
                                <div className="framer-1f9oqu1" data-framer-component-type="RichTextContainer" style={styles.s163}>
                                  <h6 className="framer-text framer-styles-preset-42t0hg" data-styles-preset="vCV2RaSbZ" dir="auto" style={styles.s164}>
                                    {"Free"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-11h22j1">
                                <LandingPrice monthly="00" yearly="00" annual={yearly} />
                                <div className="framer-1a8vhk8" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"For personal blogs and  initial testing."}
                                  </h6>
                                </div>
                              </div>
                            </div>
                            <div className="framer-i87gq4">
                              <div className="framer-1evplsw">
                                <svg className="framer-TLxVQ framer-lawvxb" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-90si9u" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"1 Website Project"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-8j5rwf">
                                <svg className="framer-TLxVQ framer-ojm0ar" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-llbg3p" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Weekly Clinical Audit"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-jrv0q8">
                                <svg className="framer-TLxVQ framer-xsibkc" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-9sgpuz" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"100 Page Crawl Limit"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5c02c7">
                                <svg className="framer-TLxVQ framer-1bfeby9" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1a8uimd" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Basic Keyword Tracking"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5yzw1p">
                                <svg className="framer-TLxVQ framer-1v70mff" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-hca7rq" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Optivio Branded Reports"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-iabj9q">
                                <svg className="framer-TLxVQ framer-fe52zd" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1ikx8v4" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Optivio branded dashboard"}
                                  </h6>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div className="framer-15noqg-container">
                            <a className="framer-wlTbG framer-11q2sx framer-v-11q2sx framer-1pauw18" data-border="true" data-framer-name="Default" href="/chat" style={styles.s168}>
                              <div className="framer-dtf4ev" data-framer-name="Text Wrapper">
                                <div className="framer-1apu6do" data-framer-component-type="RichTextContainer" style={styles.s3}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Experimentar"}
                                  </p>
                                </div>
                                <div className="framer-5sx392" data-framer-component-type="RichTextContainer" style={styles.s5}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Experimentar"}
                                  </p>
                                </div>
                              </div>
                              <div className="framer-b6t5dl" style={styles.s6}>
                                <div className="framer-1942khh">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                                <div className="framer-251h4r">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                              </div>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="framer-vy6e72-container">
                      <div className="framer-hydXV framer-vUdMM framer-1w91lyh framer-v-1w91lyh" data-framer-name="Variant 1" style={styles.s160}>
                        <div className="framer-1e3dy5k" style={styles.s161}>
                          <div className="framer-16e2h5o">
                            <div className="framer-44bnwe" data-border="true" style={styles.s162}>
                              <div className="framer-11rz544">
                                <div className="framer-1f9oqu1" data-framer-component-type="RichTextContainer" style={styles.s163}>
                                  <h6 className="framer-text framer-styles-preset-42t0hg" data-styles-preset="vCV2RaSbZ" dir="auto" style={styles.s164}>
                                    {"Starter"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-11h22j1">
                                <LandingPrice monthly="29" yearly="99" annual={yearly} />
                                <div className="framer-1a8vhk8" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"For growing startups and  small sites."}
                                  </h6>
                                </div>
                              </div>
                            </div>
                            <div className="framer-i87gq4">
                              <div className="framer-1evplsw">
                                <svg className="framer-TLxVQ framer-lawvxb" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-90si9u" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"3 Website Projects"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-8j5rwf">
                                <svg className="framer-TLxVQ framer-ojm0ar" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-llbg3p" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Daily Clinical Audits"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-jrv0q8">
                                <svg className="framer-TLxVQ framer-xsibkc" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-9sgpuz" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"1,000 Page Crawl Limit"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5c02c7">
                                <svg className="framer-TLxVQ framer-1bfeby9" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1a8uimd" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Competitor Gap Analysis"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5yzw1p">
                                <svg className="framer-TLxVQ framer-1v70mff" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-hca7rq" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Remove Optivio Branding"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-iabj9q">
                                <svg className="framer-TLxVQ framer-fe52zd" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1ikx8v4" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Unlimited Projects"}
                                  </h6>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div className="framer-15noqg-container">
                            <a className="framer-wlTbG framer-11q2sx framer-v-11q2sx framer-1pauw18" data-border="true" data-framer-name="Default" href="/chat" style={styles.s168}>
                              <div className="framer-dtf4ev" data-framer-name="Text Wrapper">
                                <div className="framer-1apu6do" data-framer-component-type="RichTextContainer" style={styles.s3}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                                <div className="framer-5sx392" data-framer-component-type="RichTextContainer" style={styles.s5}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                              </div>
                              <div className="framer-b6t5dl" style={styles.s6}>
                                <div className="framer-1942khh">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                                <div className="framer-251h4r">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                              </div>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="framer-lydd2k-container">
                      <div className="framer-hydXV framer-vUdMM framer-1w91lyh framer-v-o8vmhi" data-framer-name="Variant 2" style={styles.s169}>
                        <div className="framer-1e3dy5k" style={styles.s170}>
                          <div className="framer-16e2h5o">
                            <div className="framer-44bnwe" data-border="true" style={styles.s162}>
                              <div className="framer-11rz544">
                                <div className="framer-1f9oqu1" data-framer-component-type="RichTextContainer" style={styles.s163}>
                                  <h6 className="framer-text framer-styles-preset-42t0hg" data-styles-preset="vCV2RaSbZ" dir="auto" style={styles.s164}>
                                    {"Plus"}
                                  </h6>
                                </div>
                                <div className="framer-o3wtx6-container">
                                  <div className="framer-DIxtH framer-4F4wF framer-smmrlk framer-v-smmrlk" data-border="true" data-framer-name="Variant 1" style={styles.s171}>
                                    <div className="framer-120864l" data-framer-component-type="RichTextContainer" style={styles.s34}>
                                      <p className="framer-text framer-styles-preset-1s8g08" data-styles-preset="NxsGmJIB2" dir="auto" style={styles.s35}>
                                        {"Most popular"}
                                      </p>
                                    </div>
                                  </div>
                                </div>
                              </div>
                              <div className="framer-11h22j1">
                                <LandingPrice monthly="199" yearly="399" annual={yearly} />
                                <div className="framer-1a8vhk8" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Most Popular. For scaling  businesses."}
                                  </h6>
                                </div>
                              </div>
                            </div>
                            <div className="framer-i87gq4">
                              <div className="framer-1evplsw">
                                <svg className="framer-TLxVQ framer-lawvxb" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-90si9u" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Unlimited Projects"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-8j5rwf">
                                <svg className="framer-TLxVQ framer-ojm0ar" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-llbg3p" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Real-time Site Monitoring"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-jrv0q8">
                                <svg className="framer-TLxVQ framer-xsibkc" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-9sgpuz" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"10,000 Page Crawl Limit"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5c02c7">
                                <svg className="framer-TLxVQ framer-1bfeby9" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1a8uimd" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Full API & Webhook Access"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5yzw1p">
                                <svg className="framer-TLxVQ framer-1v70mff" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-hca7rq" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Priority Developer Support"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-iabj9q">
                                <svg className="framer-TLxVQ framer-fe52zd" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1ikx8v4" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Advanced Security & SSO"}
                                  </h6>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div className="framer-15noqg-container">
                            <a className="framer-wlTbG framer-11q2sx framer-v-11q2sx framer-1pauw18" data-border="true" data-framer-name="Default" href="/chat" style={styles.s172}>
                              <div className="framer-dtf4ev" data-framer-name="Text Wrapper">
                                <div className="framer-1apu6do" data-framer-component-type="RichTextContainer" style={styles.s3}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                                <div className="framer-5sx392" data-framer-component-type="RichTextContainer" style={styles.s5}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                              </div>
                              <div className="framer-b6t5dl" style={styles.s6}>
                                <div className="framer-1942khh">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                                <div className="framer-251h4r">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                              </div>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="framer-5p41s1-container">
                      <div className="framer-hydXV framer-vUdMM framer-1w91lyh framer-v-1w91lyh" data-framer-name="Variant 1" style={styles.s160}>
                        <div className="framer-1e3dy5k" style={styles.s161}>
                          <div className="framer-16e2h5o">
                            <div className="framer-44bnwe" data-border="true" style={styles.s162}>
                              <div className="framer-11rz544">
                                <div className="framer-1f9oqu1" data-framer-component-type="RichTextContainer" style={styles.s163}>
                                  <h6 className="framer-text framer-styles-preset-42t0hg" data-styles-preset="vCV2RaSbZ" dir="auto" style={styles.s164}>
                                    {"Enterprise"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-11h22j1">
                                <LandingPrice monthly="499" yearly="899" annual={yearly} />
                                <div className="framer-1a8vhk8" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"For agencies requiring high- volume infra."}
                                  </h6>
                                </div>
                              </div>
                            </div>
                            <div className="framer-i87gq4">
                              <div className="framer-1evplsw">
                                <svg className="framer-TLxVQ framer-lawvxb" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-90si9u" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Custom Crawl Limits"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-8j5rwf">
                                <svg className="framer-TLxVQ framer-ojm0ar" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-llbg3p" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Dedicated SEO Strategist"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-jrv0q8">
                                <svg className="framer-TLxVQ framer-xsibkc" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-9sgpuz" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Advanced Security & SSO"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5c02c7">
                                <svg className="framer-TLxVQ framer-1bfeby9" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1a8uimd" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Custom Contract & Billing"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-5yzw1p">
                                <svg className="framer-TLxVQ framer-1v70mff" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-hca7rq" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Competitor Gap Analysis"}
                                  </h6>
                                </div>
                              </div>
                              <div className="framer-iabj9q">
                                <svg className="framer-TLxVQ framer-fe52zd" role="presentation" viewBox="0 0 24 24" style={styles.s167}>
                                  <use href="#2048327766"></use>
                                </svg>
                                <div className="framer-1ikx8v4" data-framer-component-type="RichTextContainer" style={styles.s165}>
                                  <h6 dir="auto" className="framer-text" style={styles.s166}>
                                    {"Daily Clinical Audits"}
                                  </h6>
                                </div>
                              </div>
                            </div>
                          </div>
                          <div className="framer-15noqg-container">
                            <a className="framer-wlTbG framer-11q2sx framer-v-11q2sx framer-1pauw18" data-border="true" data-framer-name="Default" href="/chat" style={styles.s168}>
                              <div className="framer-dtf4ev" data-framer-name="Text Wrapper">
                                <div className="framer-1apu6do" data-framer-component-type="RichTextContainer" style={styles.s3}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                                <div className="framer-5sx392" data-framer-component-type="RichTextContainer" style={styles.s5}>
                                  <p dir="auto" className="framer-text" style={styles.s4}>
                                    {"Abrir assistente"}
                                  </p>
                                </div>
                              </div>
                              <div className="framer-b6t5dl" style={styles.s6}>
                                <div className="framer-1942khh">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                                <div className="framer-251h4r">
                                  <div style={styles.s7} data-framer-background-image-wrapper="true">
                                    <img decoding="async" loading="lazy" width="24" height="24" src="/assets/landing/eb1a8d17d83d.svg" alt="" style={styles.s8} />
                                  </div>
                                </div>
                              </div>
                            </a>
                          </div>
                        </div>
                      </div>
                    </div>
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
