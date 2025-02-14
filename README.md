> :warning: The project is messed up and stalled. It is not ready to use.
> 
> You better contact the author for consulting.

# otree-advanced-demos

The project presents a bunch of prototypical web applications for behaviorial or psycological online experiments, surveys or tests.
The apps are developed using [oTree](www.otree.org) framework and its extension [oTree-front](https://github.com/oTree-org/otree-front) (included in this repository)

The repository also contains bunch of snippets (python utilities, javascripts, styles) that can be reused in any other project unrelated to the apps.

## Features

-   Main pages of the apps are implemented in a dynamic manner for real-time interaction with low latency.
    (Contrary to traditional form-based approach that require full page reload).
-   Most of the apps run series of trials consisting of some task and expecting some response.
-   Responses of participants are immediately communicated and saved on server via live channel.
-   All the data for each trial is saved and available in 'custom export' section.
-   Where appropriate, pages measure response time with high precision (below 15ms), not affected by network latency.
-   The pages are designed in smooth animated styles, reducing visual disturbances.
-   The pages do not reveal correct or best answers, all evaluation of responses is performed on server side. That reduces possibility of cheating via inspecting page scripts and content.
