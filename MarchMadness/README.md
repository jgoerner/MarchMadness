# MarchMadness ([Kaggle Challenge](https://www.kaggle.com/c/mens-machine-learning-competition-2018))
![logo](./figures/misc/header.png)
***
## Overall Description
>Google Cloud and NCAA® have teamed up to bring you this year’s version of the Kaggle machine learning competition. Another year, another chance to anticipate the upsets, call the probabilities, and put your bracketology skills to the leaderboard test. Kagglers will join the millions of fans who attempt to forecast the outcomes of March Madness® during this year's NCAA Division I Men’s and Women’s Basketball Championships. But unlike most fans, you will pick your bracket using a combination of NCAA’s historical data and your computing power, while the ground truth unfolds on national television.
***
## How to get started
If you followed the ["wrapper" repository readme](https://github.com/jgoerner/MarchMadness#marchmadness) everything should be set up in a nicely composed docker environment. The following steps can be easily done.
### getting raw data
When entering this repository for the first time, it is useful to fetch the data from the S3 Bucket and put them into the database container. This job can be easily achieved by running the following command (from the root of this repository):
```
make data
```

After that your database container holds all the files provided by Kaggle. See the `./notebooks/` folder for further examples
on how to get common tasks done.

### visualize tables
If you start a webbrowser and open `localhost:7077` you will see the webinterface of [Apache Superset](https://superset.incubator.apache.org/). When logging in for the first time, the credentials are the superset standard credentials (usr: `admin`, pw: `superset`). If you have no experience with Superset, I encourage you to go through the following tutorials to get a grip on basic concepts before you come up with your awesome dashboard: [Building beautiful dashboards with superset](https://shuaiw.github.io/2017/08/26/building-beautiful-dashboards-with-superset.html)
Hint: The connection string for the database container is `postgres://postgres@postgres_container`.
