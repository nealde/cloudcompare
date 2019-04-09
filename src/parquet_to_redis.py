from pyspark.sql import SparkSession, DataFrame
from pyspark.ml import Pipeline, Transformer, PipelineModel
from pyspark.ml.feature import HashingTF, IDF, IDFModel, Tokenizer
from pyspark.sql.functions import udf, struct
from pyspark.sql.types import StringType
import numpy as np
from redis import StrictRedis
import zlib

sc =  SparkSession.builder.appName("Parquet to Redis").getOrCreate()

parquetpath = 's3n://neal-dawson-elli-insight-data/models/b5'


_connection = None

def connection():
    """Return the Redis connection to the URL given by the environment
    variable REDIS_URL, creating it if necessary.

    """
    global _connection
    if _connection is None:
        _connection = StrictRedis.from_url('redis://10.0.0.10:6379')
    return _connection

# CUSTOM TRANSFORMER ----------------------------------------------------------------
#class TextCleaner(Transformer):
#    """
#    A custom Transformer which drops all columns that have at least one of the
#    words from the banned_list in the name.
#    """

#    def __init__(self, inputCol='body', outputCol='cleaned_body'):
#        super(TextCleaner, self).__init__()
#         self.banned_list = banned_list
#    def clean(line):
#        line = line.lower().replace("\n"," ").replace("\r","").replace(',',"").replace(">","> ").replace("<", " <")
#        return line
#    clean_udf = udf(lambda r: clean(r), StringType())

#    def _transform(self, df: DataFrame) -> DataFrame:
#        df = df.withColumn('cleaned_body', self.clean_udf(df['body']))
#        df = df.drop('body')
    #         df = df.drop(*[x for x in df.columns if any(y in x for y in self.banned_list)])
#        return df


def store_redis(row):
    r = connection()
    tags = row['tags']
    if tags.find("|") > 0:
        tags = tags.split('|')
    idd = row['id']
    title = row['title']
    embed = row['features']
    end_idd = idd[-1:]
    front_idd = idd[:-1]

    # compress and store inds and values
    inds = zlib.compress(embed.indices.tobytes())
    vals = zlib.compress(embed.values.astype('float16').tobytes())

    r.hset('id:'+front_idd,end_idd+':t',title)
    r.hset('id:'+front_idd,end_idd+':s',str(embed.size))
    r.hset('id:'+front_idd,end_idd+':i',inds)
    r.hset('id:'+front_idd,end_idd+':v',vals)

    for tag in tags:
#         r.hset(tag+':'+idd[:2],idd[2:],1)
         r.append(trim(tag), ",id:"+idd)
    return 1
#    return to_write

#redis_udf = udf(lambda row: store_redis(row), StringType())
dd = sc.read.parquet(parquetpath).repartition(1000)
dd.createOrReplaceTempView("table1").cache()
df2 = spark.sql("SELECT field1 AS f1, field2 as f2 from table1 limit 100")
df2.collect()
#dd = dd.select('id','features','title','creation_date')
# dd = dd.withColumn('tw',redis_udf(struct([dd[x] for x in dd.columns]))).select('id','tw')\
# .select('tw').collect()
#.write.format("org.apache.spark.sql.redis").option("table", "id").option("key.column", "id").save()


#dd = sc.read.parquet(parquetpath).rdd.map(store_redis).sum()
#print(dd)

#print(dd)
#text = "<p> i am trying to create a report to display a summary of the values of the columns for each row.   a basic analogy would an inventory listing.  say i have about 15 locations like 2a 2b 2c 3a 3b 3c etc.   each location has a variety of items and the items each have a specific set of common descriptions i.e. a rating of 1-9 boolean y or n another boolean y or n.  it looks something like this:</p>   <pre> <code> 2a   4       y       n 2a   5       y       y 2a   5       n       y 2a   6       n       n       ... 2b   4       n       y   2b   4       y       y       ...etc. </code> </pre>   <p> what i would like to produce is a list of locations and summary counts of each attribute:</p>   <pre> <code> location    1 2 3 4 5 6 7 8 9      y  n        y n      total 2a                1 2 1            2  2        2 2        4 2b                2                1  1        2          2 ... ___________________________________________________________ totals            3 2 1            3  3        4 2        6 </code> </pre>   <p> the query returns fields:  </p>   <pre> <code> location_cd string   desc_cd int  y_n_1 string  y_n_2 string </code> </pre>   <p> i have tried grouping by location but cannot get the summaries to work.   i tried putting it in a table but that would only take the original query.  i tried to create datasets for each unit and create variables in each one for each of the criteria but that hasn't worked yet either.  but maybe i am way off track and crosstabs would work better?  i tried that and got a total mess the first time.  maybe a bunch of subreports?</p>   <p> can someone point me in the correct direction please?    it seemed easy when i started out but now i am getting nowhere.  i can get the report to print out the raw data but all i need are totals for each column broken down out by location.  </p> "

#dirtyData = dirtyData.withColumn('cleaned_body', clean_udf(dirtyData['body']))
#dirtyData.drop('body')
#dirtyData.cache()
#dirtyData = dirtyData.select('id','title','cleaned_body','tags','accepted_answer_id')
#dirtyData.select('cleaned_body').show()

#cleaner = TextCleaner(inputCol='body', outputCol='cleaned_body')
#dirtyData = cleaner.transform(dirtyData)

#tokenizer = Tokenizer(inputCol="cleaned_body", outputCol="words")
#hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=2**12)
#idf = IDF(inputCol="rawFeatures", outputCol="features")
#model = PipelineModel(stages=[tokenizer, hashingTF, idf])

# Fit the pipeline to training documents.
#model = pipeline.fit(dirtyData)

#idfpath = 's3n://neal-dawson-elli-insight-data/models/idf-model'
#parquetpath = 's3n://neal-dawson-elli-insight-data/models/b1'

#model = PipelineModel.load(idfpath)
#model.load(idfpath)
#model.write().overwrite().save(idfpath)
#dirtyData = model.transform(dirtyData)

#dirtyData.select('id','title','cleaned_body','features','tags').write.parquet(parquetpath)

#idftr.save(idfpath)
#try:
  #  old_data = sc.read.parquet(parquetpath)
 #   dirtyData.union(old_data)
    #SaveMode.Overwrite
#    dirtyData.select('id','title','cleaned_body','features','tags').write.mode(SaveMode.Overwrite).parquet(parquetpath)

# pyspark.sql.analysisexception
#except:
#    print("file not found - continuing")
#dirtyData.select('id','title','cleaned_body','features','tags').write.overwrite.parquet(parquetpath)
#dirtyData.select('id','title','cleaned_body','features','tags','accepted_answer_id').write.overwrite().save.parquet(parquetpath).parquet(parquetpath)

#loadedModel = IDFModel.load(idfpath)

#sentenceData = spark.createDataFrame([(0.0, text),],['label','sentence'])
#tokenizer = Tokenizer(inputCol="sentence", outputCol="words")
#wordsData = tokenizer.transform(sentenceData)

#hashingTF = HashingTF(inputCol="words", outputCol="rawFeatures", numFeatures=2**12)
#featurizedData = hashingTF.transform(wordsData)
# alternatively, CountVectorizer can also be used to get term frequency vectors
#idfPath = 'idf/'

#modelPath = "temp/idf-model"
# model.save(modelPath)
#loadedModel = IDFModel.load(modelPath)
#sample = loadedModel.transform(featurizedData).take(1)[0]['features']

#data = spark.read.format("parquet").load(parquetpath)
# tf = hashingTF.transform(words)
# tf.cache()

#rescaledData.select("_c0", "features").show()

#rescaledData.write.parquet(parquetpath)

#sample = rescaledData.select('_c0','features').take(2)[1]['features']

#def cos(a, b):
#     print(a[0].norm(2))
#    return a[0].dot(b)/(a[0].norm(2)*b.norm(2))

#sim = rescaledData.select("features").rdd.map(lambda x: cos(x, sample))
# sim = rescaledData.select("features").rdd.map(lambda x: cos(x, sample)).sortBy(lambda x: -x).take(2)


#topFive = sorted(enumerate(sim.collect()), key= lambda kv: -kv[1])[0:5]
#for idx, val in topFive:
#    print("doc '%s' has score %.4f" % (idx, val))

#normalizer = Normalizer(inputCol="features", outputCol="norm")
#data = normalizer.transform(rescaledData)

#mat = IndexedRowMatrix(data.select("_c0", "norm").rdd.map(lambda row: IndexedRow(row._c0, row.norm.toArray()))).toBlockMatrix()
#dot = mat.multiply(mat.transpose())
#dot.toLocalMatrix().toArray()