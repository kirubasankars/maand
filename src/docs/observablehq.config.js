// See https://observablehq.com/framework/config for documentation.
export default {
  // The app’s title; used in the sidebar and webpage titles.
  title: "Maand",

  // The pages and sections in the sidebar. If you don’t specify this option,
  // all pages will be listed in alphabetical order. Listing pages explicitly
  // lets you organize them into sections and have unlisted pages.
   pages: [
     {
       name: "Guide",
       pages: [
         {name: "1. Maand init", path: "/maand_init"},
         {name: "2. Agent Setup", path: "/agent_setup"},
         {name: "3. Maand run_command", path: "/run_command"},
         {name: "4. Maand build", path: "/build"},
         {name: "5. Maand update", path: "/update"},
         {name: "6. Assign Roles", path: "/assign_roles"},
         {name: "7. Job Setup", path: "/job_setup"},
         {name: "8. Job Control", path: "/job_control"},
         {name: "9. Health Check", path: "/add_health_check"},
         {name: "10. Prometheus", path: "/setup_prometheus"},
       ]
     },
     {
       name: "Insides",
       pages: [
         {name: "Agent", path: "/agent"},
         {name: "Bucket", path: "/bucket"},
         {name: "Roles", path: "/roles"},
         {name: "Job", path: "/job"},
         {name: "Allocations", path: "/allocations"},
         {name: "Job Command", path: "/job_command"},
         {name: "Health Check", path: "/health_check"},
       ]
     }
   ],

  // Content to add to the head of the page, e.g. for a favicon:
  head: '<link rel="icon" href="observable.png" type="image/png" sizes="32x32">',

  // The path to the source root.
  root: "src",

  // Some additional configuration options and their defaults:
  theme: ["near-midnight"], // try "light", "dark", "slate", etc.
  // header: "", // what to show in the header (HTML)
  // footer: "Built with Observable.", // what to show in the footer (HTML)
  // sidebar: true, // whether to show the sidebar
  // toc: true, // whether to show the table of contents
  // pager: true, // whether to show previous & next links in the footer
  // output: "dist", // path to the output root for build
  // search: true, // activate search
  // linkify: true, // convert URLs in Markdown to links
  // typographer: false, // smart quotes and other typographic improvements
  // preserveExtension: false, // drop .html from URLs
  // preserveIndex: false, // drop /index from URLs
};
