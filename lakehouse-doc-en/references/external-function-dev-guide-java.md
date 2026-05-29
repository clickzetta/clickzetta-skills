# External Function Development Guide (Java)

This document introduces how to develop UDF, UDAF, and UDTF type external functions using the Java language.
Note: External Function is currently in preview stage. You need to use the control parameters described in this document to enable it.

# UDF

Singdata Lakehouse UDF supports function development based on the Hive UDF API specification, supporting the use of GenericUDF (org.apache.hadoop.hive.ql.udf.generic.GenericUDF) and UDF (org.apache.hadoop.hive.ql.exec.UDF) for developing scalar functions.

## Developing UDF

Create a MAVEN project and add dependencies in pom.xml.

```XML
<dependency>
    <groupId>org.apache.hive</groupId>
    <artifactId>hive-exec</artifactId>
    <version>2.3.8</version>
    <scope>provided</scope>
    <exclusions>
        <exclusion>
            <groupId>org.pentaho</groupId>
            <artifactId>*</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

Write UDF code. Example:

```Java
package com.example;

import org.apache.hadoop.hive.ql.exec.UDFArgumentException;
import org.apache.hadoop.hive.ql.metadata.HiveException;
import org.apache.hadoop.hive.ql.udf.generic.GenericUDF;
import org.apache.hadoop.hive.serde2.objectinspector.ObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.PrimitiveObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.PrimitiveObjectInspector.PrimitiveCategory;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.PrimitiveObjectInspectorFactory;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.StringObjectInspector;

import java.util.Locale;

public class GenericUdfUpper extends GenericUDF {

  private StringObjectInspector soi;

  @Override
  public ObjectInspector initialize(ObjectInspector[] arguments) throws UDFArgumentException {
    checkArgsSize(arguments, 1, 1);
    checkArgPrimitive(arguments, 0);
    if (((PrimitiveObjectInspector) arguments[0]).getPrimitiveCategory() != PrimitiveCategory.STRING) {
      throw new UDFArgumentException("argument 0 requires to be string rather than " + arguments[0].getTypeName());
    }
    soi = (StringObjectInspector) arguments[0];
    return PrimitiveObjectInspectorFactory.javaStringObjectInspector;
  }

  @Override
  public Object evaluate(DeferredObject[] arguments) throws HiveException {
    Object arg = arguments[0].get();
    if (arg == null) {
      return null;
    }
    return soi.getPrimitiveJavaObject(arg).toUpperCase(Locale.ROOT);
  }

  @Override
  public String getDisplayString(String[] children) {
    return "upper";
  }
}
```

Package the project as a JAR file.

## Uploading JAR Files to Volume

Upload the packaged JAR file to an External Volume created in Singdata Lakehouse.

First, create a CONNECTION object to connect to your existing object storage address.

```SQL
-- Create a storage connection pointing to the object storage service
CREATE OR REPLACE STORAGE CONNECTION  qn_hz_bucket_ramrole
    TYPE oss
    REGION = 'cn-hangzhou'
    ROLE_ARN = 'acs:ram::1875653xxxxx:role/czudfrole'
    ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com';
```

Next, create an EXTERNAL VOLUME object to mount a specific path of the object storage.

```SQL
-- Create External Volume
CREATE EXTERNAL VOLUME qn_hz_bucket_vol
    location 'oss://qn-hz-bucket/'
    using connection qn_hz_bucket_ramrole
    directory = (
        enable=true,
        auto_refresh=false
    )
recursive=true;
```

Finally, use a local JDBC client, connect to the workspace, and use the PUT command in the local client to upload the JAR file (Note: The PUT command for uploading local files is not supported in the Studio Web-UI SQL editor).

```SQL
-- Upload the packaged UDF JAR
PUT '/Users/Downloads/upper.jar' TO  VOLUME qn_hz_bucket_vol FILE 'upper.jar';

-- View uploaded files
SHOW VOLUME DIRECTORY qn_hz_bucket_vol;

relative_path                                   url                                                                size last_modified_time  
----------------------------------------------- ------------------------------------------------------------------ ---- ------------------- 
data_parquet/data.csv                           oss://qn-hz-bucket/data_parquet/data.csv                           34   2024-05-29 17:03:25 
data_parquet/lakehouse_region_part00001.parquet oss://qn-hz-bucket/data_parquet/lakehouse_region_part00001.parquet 2472 2024-05-24 00:39:08 
upper.jar                                       oss://qn-hz-bucket/upper.jar                                       3161 2024-05-29 23:11:49 
```

You may also specify an internal volume. Although you can use an internal Volume, the code bucket parameter when creating an API CONNECTION must still point to an external address.

* **User Volume Format Address**: `volume:user://~/upper.jar`
  * `user` indicates the use of the User Volume protocol.

  * `~` indicates the current user and is a fixed value.

  * `upper.jar` indicates the target filename.
* **Table Volume Format Address**: `volume:table://table_name/upper.jar`
  * `table` indicates the use of the Table Volume protocol.
  * `table_name` indicates the table name; fill in the actual table name.
  * `upper.jar` indicates the target filename.

## Creating External Function

First, create a function compute service Connection object.

```SQL
create api connection qn_hz_fc_connection
type cloud_function 
with properties ( 
    'cloud_function.provider' = 'aliyun', 
    'cloud_function.region' = 'cn-hangzhou', 
    'cloud_function.role_arn' = 'acs:ram::1875653611111111:role/czudfrole', 
    'cloud_function.namespace' = 'default', 
    'cloud_function.code_bucket' = 'qn-hz-bucket'
);
```

Next, create the External Function, using the previously defined Volume object to read the JAR file, and using the already defined function compute connection CONNECTION object to invoke the function compute service to create a one-to-one corresponding function.

```SQL
create external function public.upper_udf 
as 'com.example.GenericUdfUpper' 
USING FILE 'volume://qn_hz_bucket_vol/upper.jar'
connection qn_hz_fc_connection
with properties ( 
         'remote.udf.api' = 'java8.hive2.v0',
          'remote.udf.protocol' = 'http.arrow.v0' 
);
```

## Test Run

Test run the UDF using test data or table data.

```SQL
-- Test run UDF
select public.upper_udf('hello') as upper;
select public.upper_udf(product_id) from product_grossing limit 50;
```

Users with Alibaba Cloud console access permissions can log into the Alibaba Cloud Function Compute console at this point to see that after the CREATE EXTERNAL FUNCTION command executes successfully, Singdata Lakehouse will automatically create the function to execute the custom function.

Executing the `DROP FUNCTION public.upper_udf;` command to delete the function will simultaneously cause the Lakehouse platform to delete the corresponding function from the cloud service provider.

# UDAF

Supports function development based on the Hive 2.x UDAF specification, using [GenericUDAFResolver](https://github.com/apache/hive/blob/branch-2.3/ql/src/java/org/apache/hadoop/hive/ql/udf/generic/GenericUDAFResolver.java) and [GenericUDAFEvaluator](https://github.com/apache/hive/blob/branch-2.3/ql/src/java/org/apache/hadoop/hive/ql/udf/generic/GenericUDAFEvaluator.java) to develop UDAF.

UDAF function runtime environment:

Java: version 1.8 (JDK distribution provided by the cloud provider's function compute service runtime environment).

Create a MAVEN project and add dependencies in pom.xml.

```XML
<dependency>
    <groupId>org.apache.hive</groupId>
    <artifactId>hive-exec</artifactId>
    <version>2.3.8</version>
    <scope>provided</scope>
    <exclusions>
        <exclusion>
            <groupId>org.pentaho</groupId>
            <artifactId>*</artifactId>
        </exclusion>
    </exclusions>
</dependency>
```

## UDAF Development

Write UDAF code based on GenericUDAFResolver and GenericUDAFEvaluator.

```SQL
package com.example;

import org.apache.hadoop.hive.ql.exec.UDFArgumentTypeException;
import org.apache.hadoop.hive.ql.metadata.HiveException;
import org.apache.hadoop.hive.ql.parse.SemanticException;
import org.apache.hadoop.hive.ql.udf.generic.AbstractGenericUDAFResolver;
import org.apache.hadoop.hive.ql.udf.generic.GenericUDAFEvaluator;
import org.apache.hadoop.hive.serde2.objectinspector.ObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.PrimitiveObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.PrimitiveObjectInspector.PrimitiveCategory;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.IntObjectInspector;
import org.apache.hadoop.hive.serde2.objectinspector.primitive.PrimitiveObjectInspectorFactory;
import org.apache.hadoop.hive.serde2.typeinfo.PrimitiveTypeInfo;
import org.apache.hadoop.hive.serde2.typeinfo.TypeInfo;

public class sumint extends AbstractGenericUDAFResolver {

    @Override
    public GenericUDAFEvaluator getEvaluator(TypeInfo[] info) throws SemanticException {

        if (info.length != 1) {
            throw new UDFArgumentTypeException(info.length - 1, "Exactly one argument is expected.");
        }

        if (info[0].getCategory() != ObjectInspector.Category.PRIMITIVE) {
            throw new UDFArgumentTypeException(0, "Only primitive type arguments are accepted but " + info[0].getTypeName() + " was passed as parameter 1.");
        }

        if (((PrimitiveTypeInfo)info[0]).getPrimitiveCategory() == PrimitiveCategory.STRING) {
            return new SumStringEvaluator();
        } else if (((PrimitiveTypeInfo)info[0]).getPrimitiveCategory() == PrimitiveCategory.INT) {
            return new SumIntEvaluator();
        } else {
            throw new UDFArgumentTypeException(0, "Only string, int type arguments are accepted but " + info[0].getTypeName() + " was passed as parameter 1.");
        }
    }


    public static class SumStringEvaluator extends GenericUDAFEvaluator {

        private PrimitiveObjectInspector inputOI;

        static class SumAggregationBuffer implements AggregationBuffer {
            int sum;
        }

        @Override
        public ObjectInspector init(Mode m, ObjectInspector[] parameters) throws HiveException {
            super.init(m, parameters);

            inputOI = (PrimitiveObjectInspector) parameters[0];
            return PrimitiveObjectInspectorFactory.javaIntObjectInspector;
        }

        @Override
        public AggregationBuffer getNewAggregationBuffer() throws HiveException {
            SumAggregationBuffer sum = new SumAggregationBuffer();
            reset(sum);
            return sum;
        }

        @Override
        public void reset(AggregationBuffer agg) throws HiveException {
            ((SumAggregationBuffer) agg).sum = 0;
        }

        @Override
        public void iterate(AggregationBuffer agg, Object[] parameters) throws HiveException {
            if(parameters.length != 0 && inputOI.getPrimitiveJavaObject(parameters[0]) != null) {
                ((SumAggregationBuffer) agg).sum += Integer.parseInt(inputOI.getPrimitiveJavaObject(parameters[0]).toString());
            }
        }

        @Override
        public Object terminatePartial(AggregationBuffer agg) throws HiveException {
            return ((SumAggregationBuffer) agg).sum;
        }

        @Override
        public void merge(AggregationBuffer agg, Object partial) throws HiveException {
            ((SumAggregationBuffer) agg).sum += Integer.parseInt(inputOI.getPrimitiveJavaObject(partial).toString());
        }

        @Override
        public Object terminate(AggregationBuffer agg) throws HiveException {
            return ((SumAggregationBuffer) agg).sum;
        }

    }

    public static class SumIntEvaluator extends GenericUDAFEvaluator {

        private IntObjectInspector inputOI;

        static class SumAggregationBuffer implements AggregationBuffer {
            int sum;
        }

        @Override
        public ObjectInspector init(Mode m, ObjectInspector[] parameters) throws HiveException {
            super.init(m, parameters);

            inputOI = (IntObjectInspector) parameters[0];
            return PrimitiveObjectInspectorFactory.javaIntObjectInspector;
        }

        @Override
        public AggregationBuffer getNewAggregationBuffer() throws HiveException {
            SumAggregationBuffer sum = new SumAggregationBuffer();
            reset(sum);
            return sum;
        }

        @Override
        public void reset(AggregationBuffer agg) throws HiveException {
            ((SumAggregationBuffer) agg).sum = 0;
        }

        @Override
        public void iterate(AggregationBuffer agg, Object[] parameters) throws HiveException {
            ((SumAggregationBuffer) agg).sum += inputOI.get(parameters[0]);
        }

        @Override
        public Object terminatePartial(AggregationBuffer agg) throws HiveException {
            return ((SumAggregationBuffer) agg).sum;
        }

        @Override
        public void merge(AggregationBuffer agg, Object partial) throws HiveException {
            ((SumAggregationBuffer) agg).sum += inputOI.get(partial);
        }

        @Override
        public Object terminate(AggregationBuffer agg) throws HiveException {
            return ((SumAggregationBuffer) agg).sum;
        }

    }
}
```

## Uploading JAR Files to Volume

Compile and package into a JAR, then upload to the user-specified object storage location or Lakehouse Volume object.

```SQL
-- Upload the packaged UDF JAR
PUT '/Users/Downloads/sumint.jar' TO  VOLUME qn_hz_bucket_vol FILE 'sumint.jar';

-- View uploaded files
SHOW VOLUME DIRECTORY qn_hz_bucket_vol;

relative_path url                           size last_modified_time  
------------- ----------------------------- ---- ------------------- 
upper.jar     oss://qn-hz-bucket/upper.jar  3161 2024-05-29 23:11:49 
sumint.jar    oss://qn-hz-bucket/sumint.jar 1022 2024-05-30 01:10:28 
```

## Creating External Function

1.  Create a Connection object connecting to the function compute service (see the introduction in the UDF section)
2. Create the external function in the LakeHouse system

UDAF External Function creation syntax:

```SQL
CREATE EXTERNAL FUNCTION public.<funcName>
    AS '<className>'
    USING FILE 'oss://<bucket>/<pathToJar>'
    CONNECTION <connectionName>
    WITH PROPERTIES (
        'remote.udf.api' = 'java8.hive2.v0', 
        'remote.udf.category' = 'AGGREGATOR');
```

Parameter description:

1. functionName: Any valid identifier can be used, e.g., my\_agg
2. className: Fill in the fully qualified class name of the GenericUDAFResolver developed in Step 1, e.g., com.example.GenericUDAFSum;
3. bucket and pathToJar: Fill in the OSS bucket and object path uploaded in Step 2;
4. connectionName: Use the name of the connection created in Step 3, e.g., udf\_deploy\_0317;
5. Keep the last two PROPERTIES as-is;

Example:

```SQL
-- Create External Function
create external function public.sumint
as 'com.example.sumint' 
USING FILE 'volume://qn_hz_bucket_vol/sumint.jar'
connection qn_hz_fc_connection
with properties ( 
         'remote.udf.api' = 'java8.hive2.v0',
         'remote.udf.category' = 'AGGREGATOR'
);
```

## Test Run

Test run the UDF using test data or table data. Note: Currently, remote function access needs to be enabled via the `cz.sql.remote.udf.enabled` parameter.

```SQL
-- Test run UDF
set cz.sql.remote.udf.enabled = true;
select public.sumint(amount) from product_grossing;
```

# UDTF

## UDTF Development

Supports developing UDTF by extending org.apache.hadoop.hive.ql.udf.generic.GenericUDTF. UDTF needs to implement three methods: initialize, process, and close. UDTF first calls the initialize method, which returns the information of the UDTF's output rows (number of returned columns, types). After initialization, the process method is called to process the input parameters, and results can be returned via the forward() method. Finally, the close() method is called to clean up resources that need cleanup.

Write UDTF code. Example:

```Java
package com.example;

import org.apache.hadoop.hive.ql.exec.UDFArgumentException;
import org.apache.hadoop.hive.ql.metadata.HiveException;
import org.apache.hadoop.hive.ql.udf.generic.GenericUDTF;
import org.apache.hadoop.hive.serde2.objectinspector.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;

public class MyExplode extends GenericUDTF {

    private static Logger logger = LoggerFactory.getLogger(MyExplode.class);
    private ObjectInspector oi;
    private Object[] params;

    @Override
    public StructObjectInspector initialize(ObjectInspector[] argOIs) throws UDFArgumentException {

        oi = argOIs[0];
        final ObjectInspector.Category category = oi.getCategory();

        List<String> names = new ArrayList<>(2);
        List<ObjectInspector> types = new ArrayList<>(2);
        switch (category){

            case MAP:
                logger.info("receive explode category : Map");
                names.add("key");
                names.add("value");
                final MapObjectInspector moi = (MapObjectInspector) this.oi;
                types.add(moi.getMapKeyObjectInspector());
                types.add(moi.getMapValueObjectInspector());
                params = new Object[2];
                break;
            case LIST:
                logger.info("receive explode category : List");
                names.add("value");
                final ListObjectInspector loi = (ListObjectInspector) oi;
                types.add(loi.getListElementObjectInspector());
                params = new Object[1];
                break;
            default:
                throw new UDFArgumentException("not supported category for function explode : " + category);
        }
        return ObjectInspectorFactory.getStandardStructObjectInspector(names,types);
    }

    @Override
    public void process(Object[] args) throws HiveException {

        if (args.length != 1 || Objects.isNull(args[0])){


            throw new HiveException("Only 1 nonnull arg supported for function explode, but got " + args.length);
        }
        ObjectInspector.Category category = oi.getCategory();
        switch(category){

            case MAP:
                final Map<?, ?> map = ((MapObjectInspector) oi).getMap(args[0]);
                final Iterator<? extends Map.Entry<?, ?>> it = map.entrySet().iterator();
                while(it.hasNext()){

                    final Map.Entry<?, ?> entry = it.next();
                    params[0] = entry.getKey();
                    params[1] = entry.getValue();
                    forward(params);
                }
                break;
            case LIST:
                final List<?> list = ((ListObjectInspector) oi).getList(args[0]);
                final Iterator<?> itl = list.iterator();
                while (itl.hasNext()) {


                    params[0] = itl.next();
                    forward(params);
                }
                break;
        }
    }

    @Override
    public void close() throws HiveException {

        oi = null;
        for (int i = 0; i < params.length; i++) {
            params[i] = null;
        }
        params = null;
    }
}
```

## Uploading JAR Files to Volume

Compile and package into a JAR, then upload to the user-specified object storage location or Lakehouse Volume object.

```SQL
-- Upload the packaged UDF JAR
PUT '/Users/Downloads/MyExplode.jar' TO  VOLUME qn_hz_bucket_vol FILE 'MyExplode.jar';
```

## Creating External Function

1.  Create a Connection object connecting to the function compute service (see the introduction in the UDF section)
2. Create the external function in the LakeHouse system

UDTF External Function creation syntax:

```SQL
CREATE EXTERNAL FUNCTION public.<funcName>
    AS '<className>'
    USING FILE 'oss://<bucket>/<pathToJar>'
    CONNECTION <connectionName>
    WITH PROPERTIES (
        'remote.udf.api' = 'java8.hive2.v0', 
        'remote.udf.category' = 'TABLE_VALUED');
```

Parameter description:

1. functionName: Any valid identifier can be used, e.g., my\_udtf
2. className: Fill in the fully qualified class name of the GenericUDTF developed in Step 1, e.g., com.example.MyGenericUDTF;
3. bucket and pathToJar: Fill in the OSS bucket and object path uploaded in Step 2;
4. connectionName: Use the name of the connection created in Step 3, e.g., my\_function\_conn;
5. Keep the last two PROPERTIES as-is;

^
