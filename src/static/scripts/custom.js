const searchAndHideOperations = (value) => {
  const operationAccordians = document.querySelectorAll(".opblock-tag");
  for (const accordian of operationAccordians) {
    const operationName = accordian.getAttribute("id").split("operations-tag-")[1];
    // Finds all routes that have an ID that starts with the block name
    const routes = document.querySelectorAll("[id^='operations-" + operationName + "']");
    let hiddenRoutesTotal = 0;
    for (const route of routes) {
      const path = route.querySelector(".opblock-summary-path").getAttribute("data-path");
      const method = route.querySelector(".opblock-summary-method").innerText;
      const description = route.querySelector(".opblock-summary-description").innerText;
      const shouldDisplay =
        path.toLowerCase().includes(value) ||
        method.toLowerCase().includes(value) ||
        description.toLowerCase().includes(value);  
      
      if (shouldDisplay) {
        route.style.display = "block";
      } else {
        route.style.display = "none";
        hiddenRoutesTotal++;
      }
    }
    // If all routes are hidden, hide the entire accordian
    accordian.style.display = hiddenRoutesTotal === routes.length ? "none" : "block";
  }
};

const shownModels = [
  "CashFlow",
  "Activity",
  "Account",
  "File",
  "FinancialValue",
  "Holding",
  "InvestingEntity",
  "WireInstructions",
  "IssuingEntity",
  "Lookthrough",
  "Offering",
  "Task",
  "User",
];

const searchAndHideModels = (value) => {
  // Disabling model filtering so project-specific schemas are visible
  const models = document.querySelectorAll("[id^='model-']");
  for (const model of models) {
    model.style.display = "block";
  }
};

const searchAndHideDescription = (value) => {
  /**
   * The description renders as a series of HTML elements, so there's no "scoping" that we
   * could use to easily group a heading and text. We've gotta iterate through the elements
   * and determine which are related. As we proceed through the elements, encountering
   * a heading is a signal that we're starting a new section. We'll hide the previous
   */
  const groups = [...document.querySelectorAll("td")];
  for (const group of groups) {
    console.log(group,"group");
    if (group.classList.contains("response-col_status") || group.classList.contains("response-col_description")) {
      continue;
    }
    const markdownElements = [...group.children];
    let groupHadShown = false;
    let sectionHadShown = false;
    let sectionElementCollection = [];
    const hideOrShowSectionAndReset = () => {
      for (const elementInSection of sectionElementCollection) {
        if (sectionHadShown) {
          elementInSection.style.display = "block";
        } else {
          elementInSection.style.display = "none";
        }
      }
      sectionHadShown = false;
      sectionElementCollection = [];
    };
    for (const element of markdownElements) {
      if (element.tagName === "H2" || element.tagName === "H3") {
        hideOrShowSectionAndReset();
      } else if (element.tagName === "IMG" || element.tagName === "PRE") {
        sectionHadShown = value === "";
        groupHadShown = value === "";
        sectionElementCollection.push(element);
        hideOrShowSectionAndReset();
        break;
      }
      if (element.innerText.toLowerCase().includes(value)) {
        sectionHadShown = true;
        groupHadShown = true;
      }
      sectionElementCollection.push(element);
    }
    // Once we're here, there still a section that's been collected, but not processed,
    // since there no more headings to trigger the hiding behavior. We need to explicitly
    // hide or show the last section.
    hideOrShowSectionAndReset();
    if (groupHadShown) {
      group.style.display = "table-cell";
    } else {
      group.style.display = "none";
    }
  }
};

const createSearchBar = () => {
  const input = document.createElement("input");
  input.classList.add("search-bar");
  input.placeholder = "Search";
  input.oninput = function (e) {
    const rows = document.querySelectorAll("tr");
    const value = e.target.value.toLowerCase();
    if (value === "") {
    } else {
      for (const row of rows) {
        row.style.borderTop = "none";
      }
    }
    searchAndHideDescription(value);
    searchAndHideOperations(value);
    searchAndHideModels(value);
  };
  return input;
};

/**
 * Since we're not in control of the actual index.html, we
 * need to dynamically replace the logo with the Arch logo
 */
const changeToArchLogo = (parent) => {
  const logo = parent.querySelector("img");
  if (logo) {
    logo.src = "/static/images/arch-logo.svg";
    logo.height = "20";
    logo.style.display = "block";
  }
};

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text).then(() => {
    console.log("Copied to clipboard");
  }).catch(err => {
    console.error("Failed to copy!", err);
  });
};

const downloadAsFile = (filename, text) => {
  const blob = new Blob([text], { type: "application/json" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
};

const addResponseActionButtons = (responseBlock) => {
  if (responseBlock.querySelector(".response-actions")) return;

  const codeBlock = responseBlock.querySelector("pre");
  if (!codeBlock) return;

  const actionsContainer = document.createElement("div");
  actionsContainer.className = "response-actions";

  const copyBtn = document.createElement("button");
  copyBtn.className = "btn response-action-btn";
  copyBtn.innerText = "Copy";
  copyBtn.onclick = () => copyToClipboard(codeBlock.innerText);

  const downloadBtn = document.createElement("button");
  downloadBtn.className = "btn response-action-btn";
  downloadBtn.innerText = "Download";
  downloadBtn.onclick = () => {
    const filename = `response_${new Date().getTime()}.json`;
    downloadAsFile(filename, codeBlock.innerText);
  };

  actionsContainer.appendChild(copyBtn);
  actionsContainer.appendChild(downloadBtn);
  
  // Insert buttons at the top of the pre block or its container
  codeBlock.parentNode.insertBefore(actionsContainer, codeBlock);
};

/**
 * Custom JS seems to be immediately executed, so we need to wait for
 * the Swagger UI's built in scripts to execute and populate the
 * page before we can start manipulating it.
 */
const initializationPolling = setInterval(function () {
  const topbar = document.querySelector(".topbar-wrapper");
  if (topbar) {
    console.log("Custom UI: Topbar found!");
    try {
      clearInterval(initializationPolling);
      changeToArchLogo(topbar);
      console.log("Custom UI: Logo changed (or checked)");
      const searchBar = createSearchBar();
      searchBar.id = "custom-search-bar";
      const logoLink = topbar.querySelector('a.link');
      if (logoLink) {
        logoLink.after(searchBar);
      } else {
        topbar.prepend(searchBar);
      }
      console.log("Custom UI: Search bar injected after logo");

      document.body.insertAdjacentHTML(
        "beforeend",
        `
        <div id="modal">
          <div id="modal-body">
            <img src="" id="modal-image" />
          </div>
        </div>
      `
      );
      const modal = document.getElementById("modal");
      if (modal) {
        modal.addEventListener("click", (e) => {
          modal.style.display = "none";
          document.documentElement.style.overflowY = "scroll";
        });
      }

      searchAndHideModels("");

      const images = document.querySelectorAll("td > img");
      for (const image of images) {
        image.addEventListener("click", (e) => {
          const modalImg = document.getElementById("modal-image");
          if (modalImg && modal) {
            modalImg.setAttribute("src", e.target.getAttribute("src"));
            modal.style.display = "flex";
            modal.style.top = `${window.scrollY}px`;
            document.documentElement.style.overflowY = "hidden";
          }
        });
      }

      // Any spans with [...] are schemas that can be expanded (which only have 1 depth level). Expand them!
      const schemaExpanderObserver = new MutationObserver(() => {
        [...document.querySelectorAll("span")]
          .filter((a) => a.textContent === "[...]")
          .forEach((a) => a.click());
      });
      schemaExpanderObserver.observe(document.body, {
        childList: true,
        subtree: true,
      });

      // Observer for response blocks to add Copy/Download buttons
      const responseObserver = new MutationObserver(() => {
        const responseBlocks = document.querySelectorAll(".response-col_description");
        for (const block of responseBlocks) {
          addResponseActionButtons(block);
        }
      });
      responseObserver.observe(document.body, {
        childList: true,
        subtree: true,
      });

      // We listen for any changes to any of the route blocks, and clone the code
      // block so it can be side by side with the schema
      const codeAndSchemaSideBySideObserver = new MutationObserver((e) => {
        const optBodies = [...document.body.querySelectorAll(".opblock")];
        for (const newOptBlock of optBodies) {
          // If we've already applied side-by-side, or if "Try it out" is active (cancel button exists), skip
          const isTryItOutActive = !!newOptBlock.querySelector(".btn-group .cancel");
          if (newOptBlock.classList.contains("side-by-side-applied") || isTryItOutActive) {
            continue;
          }

          const code = newOptBlock.querySelector(".highlight-code");
          if (code) {
            const schemaButton = newOptBlock.querySelector(
              "[aria-selected='false'][data-name='model']"
            );
            
            // Check if we are in the "Request body" or "Parameters" section where the side-by-side logic makes sense
            // and ensure we don't move things if the user is already interacting with the body param textarea
            const bodyParamTextArea = newOptBlock.querySelector(".body-param__text");
            if (schemaButton && !bodyParamTextArea) {
              const exampleButton = newOptBlock.querySelector(
                "[data-name='example']"
              );
              
              code.style.width = "35%";
              schemaButton.click();
              
              const modelBox = newOptBlock.querySelector(".model-box");
              if (modelBox) {
                modelBox.style.width = "60%";
                // Force modelBox to be block, otherwise it might be hidden when we switch back to example
                modelBox.style.display = "block";
                
                modelBox.insertAdjacentElement("beforebegin", code);
                const modelPanel = newOptBlock.querySelector("[data-name='modelPanel']");
                if (modelPanel) {
                  modelPanel.style.display = "flex";
                  modelPanel.style.justifyContent = "space-evenly";
                }
                
                // Switch back to Example Value tab so "Try it out" works on first click
                if (exampleButton) {
                  exampleButton.click();
                }

                // Instead of removing the tablist, just hide it
                const tabList = newOptBlock.querySelector("[role='tablist']");
                if (tabList) {
                  tabList.style.display = "none";
                }

                newOptBlock.classList.add("side-by-side-applied");
              }
            }
          }
        }
      });
      // Swagger hides and shows content by inserting / removing directly from the dom. We use an observer here
      // to catch exactly when the endpoint block is mutated and perform our own additional logic to clone and render
      // both schema + example value if they exist.
      for (const node of [...document.body.querySelectorAll(".opblock")]) {
        codeAndSchemaSideBySideObserver.observe(node, {
          childList: true,
          subtree: true,
        });
      }
    } catch (e) {
      console.error("Error during custom JS initialization:", e);
    }
  }
}, 50);
