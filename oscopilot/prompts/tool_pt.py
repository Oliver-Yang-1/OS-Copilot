function_overview = """
### Function Overview

1. **`clickElement(xpath)`**  
   - **Purpose**: Clicks the first element that matches the provided XPath.
   - **Usage**: Pass an XPath expression as a string to the function.
   - **Example**: `clickElement("//div[@id='button']");`
   - **Notes**: Only the first matching element will be clicked. If no element is found, an error message is logged.

2. **`clickElements(xpath)`**  
   - **Purpose**: Clicks all elements that match the provided XPath.
   - **Usage**: Pass an XPath expression as a string to the function.
   - **Example**: `clickElements("//button[@class='clickable']");`
   - **Notes**: All matching elements will be clicked. If no elements are found, an error message is logged.

3. **`simulateMouseEvent(xpath)`**  
   - **Purpose**: Simulates a series of mouse events (`mousedown`, `mouseup`, `click`) on all elements that match the provided XPath.
   - **Usage**: Pass an XPath expression as a string to the function.
   - **Example**: `simulateMouseEvent("//div[@class='clickable-area']");`
   - **Notes**: The function dispatches `mousedown`, `mouseup`, and `click` events in sequence for each matching element. If no elements are found, an error message is logged.

4. **`extractTextByXPath(xpath)`**  
   - **Purpose**: Extracts and returns the text content of all elements that match the provided XPath.
   - **Usage**: Pass an XPath expression as a string to the function. The result will be an array of text contents.
   - **Example**: `let texts = extractTextByXPath("//div[@class='content']");`
   - **Notes**: The function returns an array of text values from all matching elements.

5. **`downloadJSON(data, filename)`**  
   - **Purpose**: Downloads a JSON file containing the provided `data` with the specified `filename`.
   - **Usage**: Pass an object as `data` and a string as `filename` to download the data as a `.json` file.
   - **Example**: `downloadJSON({name: "John", age: 30}, 'data.json');`
   - **Notes**: The function creates a downloadable `.json` file with the provided content. This works by creating an invisible anchor (`<a>`) element and triggering the download.

6. **`scrollDown(pixels, interval = 100, totalDuration = 2000)`**  
   - **Purpose**: Scrolls the page down by the specified `pixels`, over a specified `interval` and `totalDuration`.
   - **Usage**: Pass the number of pixels to scroll, and optionally, the interval and total duration for the scroll.
   - **Example**: `scrollDown(500); // Scrolls down by 500 pixels`
   - **Notes**: The function scrolls the page smoothly over the specified time. If no interval or total duration is provided, it defaults to 100ms and 2000ms, respectively.

7. **`delay(ms)`**  
   - **Purpose**: Returns a Promise that resolves after the specified `ms` delay.
   - **Usage**: Call this function with the desired delay time in milliseconds, and use it with `await` in an `async` function.
   - **Example**: `await delay(1000); // Waits for 1 second`
   - **Notes**: This function is `async` and should be used with `await` to pause the execution of subsequent code.

8. **`simulateKeyPress(key)`**  
   - **Purpose**: Simulates a keyboard key press for the specified `key`.
   - **Usage**: Pass the key to be pressed (as a string) to the function.
   - **Example**: `simulateKeyPress('Enter');`
   - **Notes**: The function simulates the `keydown` and `keyup` events for the specified key. The key is passed as a string (e.g., `'Enter'`, `'a'`, `'1'`). The key events are triggered with a 100ms delay between `keydown` and `keyup` to simulate an actual key press and release.

"""

code_prefix = '''
    function clickElement(xpath) {
  // Evaluate the XPath to get all matching elements
  const result = document.evaluate(
    xpath,
    document,
    null,
    XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
    null
  );

  // Loop through all matching elements
  if (result.snapshotLength > 0) {
    for (let i = 0; i < result.snapshotLength; i++) {
      const element = result.snapshotItem(i);
      if (element) {
        // Trigger a click on each element
        element.click();
        console.log(`Clicked element ${i + 1}`);
        return;
      }
    }
  } else {
    console.error("No elements found for the provided XPath.");
  }
}

function clickElements(xpath) {
  // Evaluate the XPath to get all matching elements
  const result = document.evaluate(
    xpath,
    document,
    null,
    XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
    null
  );

  // Loop through all matching elements
  if (result.snapshotLength > 0) {
    for (let i = 0; i < result.snapshotLength; i++) {
      const element = result.snapshotItem(i);
      if (element) {
        // Trigger a click on each element
        element.click();
        console.log(`Clicked element ${i + 1}`);
      }
    }
  } else {
    console.error("No elements found for the provided XPath.");
  }
}

function simulateMouseEvent(xpath) {
  // Evaluate the XPath to get all matching elements
  const result = document.evaluate(
    xpath,
    document,
    null,
    XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
    null
  );

  // Loop through all matching elements
  if (result.snapshotLength > 0) {
    for (let i = 0; i < result.snapshotLength; i++) {
      const element = result.snapshotItem(i);
      if (element) {
        // Create and dispatch the mousedown event
        const mouseDownEvent = new MouseEvent('mousedown', {
          bubbles: true,
          cancelable: true,
          view: window
        });
        element.dispatchEvent(mouseDownEvent);

        // Create and dispatch the mouseup event
        const mouseUpEvent = new MouseEvent('mouseup', {
          bubbles: true,
          cancelable: true,
          view: window
        });
        element.dispatchEvent(mouseUpEvent);

        // Create and dispatch the click event
        const clickEvent = new MouseEvent('click', {
          bubbles: true,
          cancelable: true,
          view: window
        });
        element.dispatchEvent(clickEvent);

        console.log(`Simulated mouse event on element ${i + 1}`);
      }
    }
  } else {
    console.error("No elements found for the provided XPath.");
  }
}

function extractTextByXPath(xpath) {
  const result = [];
  const xpathResult = document.evaluate(
    xpath,
    document,
    null,
    XPathResult.ORDERED_NODE_ITERATOR_TYPE,
    null
  );

  let node = xpathResult.iterateNext();
  while (node) {
    result.push(node.textContent.trim());
    node = xpathResult.iterateNext();
  }
  return result;
}

function downloadJSON(data, filename) {
  // Convert data to JSON string
  const jsonData = JSON.stringify(data, null, 2); // Pretty print JSON with 2 spaces
  // Create a Blob from the JSON data
  const blob = new Blob([jsonData], {type: 'application/json'});
  // Create a link element
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename; // Set the filename for the download
  a.style.display = 'none';
  // Append the link to the document, trigger the download, then remove it
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

function simulateKeyPress(key) {
  // Create a new KeyboardEvent for the keydown event
  const keyDownEvent = new KeyboardEvent('keydown', {
    key: key,            // The key that is pressed
    code: key,           // The physical key code
    keyCode: key.charCodeAt(0),  // The keyCode of the key (for compatibility)
    bubbles: true,       // Allow event to propagate
    cancelable: true,    // Allow event to be canceled
    view: window         // The window in which the event is dispatched
  });

  // Create a new KeyboardEvent for the keyup event
  const keyUpEvent = new KeyboardEvent('keyup', {
    key: key,
    code: key,
    keyCode: key.charCodeAt(0),
    bubbles: true,
    cancelable: true,
    view: window
  });

  // Dispatch the keydown event
  document.dispatchEvent(keyDownEvent);

  // Dispatch the keyup event after a short delay (to simulate holding and releasing the key)
  setTimeout(() => {
    document.dispatchEvent(keyUpEvent);
  }, 100); // Delay of 100ms between keydown and keyup
}


function scrollDown(pixels, interval = 100, totalDuration = 2000) {
  let scrolled = 0;
  const step = (pixels / (totalDuration / interval));

  const scrollInterval = setInterval(() => {
    if (scrolled >= pixels) {
      clearInterval(scrollInterval); // Stop scrolling after the total pixels are reached
    } else {
      window.scrollBy(0, step); // Scroll down by step
      scrolled += step;
    }
  }, interval);
}
'''

prompt = {
    "generate_javascript": """
    # Generate Javascript code to complete the task {task_description}.

    code output Format:
    ```Javascript
    Javascript code
    ```
    """,
    "generate_spider_javascript": f"""
You are tasked with generating JavaScript code for web scraping (spider) purposes. Given the following task description, create JavaScript code that interacts with a webpage, extracts the necessary data, and optionally handles pagination or clicks to load more content. The task may involve extracting text, links, or attributes from specific elements or interacting with the page (e.g., clicking buttons, selecting dropdowns, or scrolling). The code should be designed to work in a modern browser environment, and any necessary DOM manipulations should be handled efficiently.

### Function Overview:
{function_overview}

The JavaScript code should include appropriate functions for extracting data from the page, handling dynamic content, and optionally downloading the extracted data as a JSON file. Make sure the code is well-structured and includes comments where necessary to explain what each part of the code does.

For example:
1. If the task involves clicking elements, ensure that the relevant function is implemented for that purpose.
2. If the task involves scrolling, ensure that a scroll-down mechanism is in place to load content.
3. If the task requires extracting specific text from elements, ensure that the extraction is done using XPath or appropriate DOM selectors.

The generated code should be clean, modular, and focused on the specific task outlined in the description. The code should be ready to be executed directly in a browser's developer console or as part of a browser automation script.
""",
    "code_prefix": code_prefix
}
