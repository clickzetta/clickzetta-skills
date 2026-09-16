# External Function Development Guide (Java)

This document explains how to develop UDF, UDAF, and UDTF External Functions using Java.
Note: External Function is currently in preview. You must enable it using the control parameter described in this document.

## UDF

Singdata Lakehouse UDF supports developing functions based on the Hive UDF API specification. You can use GenericUDF (`org.apache.hadoop.hive.ql.udf.generic.GenericUDF`) and UDF (`org.apache.hadoop.hive.ql.exec.UDF`) to develop scalar functions.

### Developing a UDF

Create a Maven project and add the dependency to `pom.xml`.

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

Write the UDF code. Example:

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

### Upload the JAR File to a Volume

Upload the packaged JAR file to an External Volume created in Singdata Lakehouse.

First, create a CONNECTION object to connect to your existing object storage location.

```SQL
-- Create a storage connection definition pointing to object storage
CREATE OR REPLACE STORAGE CONNECTION  qn_hz_bucket_ramrole
    TYPE oss
    REGION = 'cn-hangzhou'
    ROLE_ARN = 'acs:ram::1875653xxxxx:role/czudfrole'
    ENDPOINT = 'oss-cn-hangzhou-internal.aliyuncs.com';
```

Next, create an EXTERNAL VOLUME object to mount a specific path in object storage.

```SQL
-- Create an External Volume
CREATE EXTERNAL VOLUME qn_hz_bucket_vol
    location 'oss://qn-hz-bucket/'
    using connection qn_hz_bucket_ramrole
    directory = (
        enable=true,
        auto_refresh=false
    )
recursive=true;
```

Finally, use a local JDBC client to connect to the workspace and upload the JAR file using the PUT command from your local client (note: the PUT command for uploading local files is not supported in the Studio Web UI SQL editor).

```SQL
-- Upload the packaged UDF JAR
PUT '/Users/Downloads/upper.jar' TO  VOLUME qn_hz_bucket_vol FILE 'upper.jar';

-- View the uploaded files
SHOW VOLUME DIRECTORY qn_hz_bucket_vol;

relative_path                                   url                                                                size last_modified_time  
----------------------------------------------- ------------------------------------------------------------------ ---- ------------------- 
data_parquet/data.csv                           oss://qn-hz-bucket/data_parquet/data.csv                           34   2024-05-29 17:03:25 
data_parquet/lakehouse_region_part00001.parquet oss://qn-hz-bucket/data_parquet/lakehouse_region_part00001.parquet 2472 2024-05-24 00:39:08 
upper.jar                                       oss://qn-hz-bucket/upper.jar                                       3161 2024-05-29 23:11:49 
```

You can also specify an internal volume. Although you can use an internal Volume, the `code bucket` parameter in your API CONNECTION must still be set to an external address.

* **User Volume address format**: `volume:user://~/upper.jar`
  * `user` indicates the User Volume protocol.
  * `~` represents the current user and is a fixed value.
  * `upper.jar` is the target file name.
* **Table Volume address format**: `volume:table://table_name/upper.jar`
  * `table` indicates the Table Volume protocol.
  * `table_name` is the table name; fill in the actual table name.
  * `upper.jar` is the target file name.

### Create an External Function

First, create a Connection object for the Function Compute service.

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

Next, create the External Function. Use the Volume object defined earlier to read the JAR file, and use the Connection object for the Function Compute service to create a corresponding function.

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

### Test Run

Test the UDF with sample data or table data.

```SQL
-- Test run the UDF
select public.upper_udf('hello') as upper;
select public.upper_udf(product_id) from product_grossing limit 50;
```

Users with access to the Alibaba Cloud console can log in to the Alibaba Cloud Function Compute console to verify that after the CREATE EXTERNAL FUNCTION command executes successfully, Singdata Lakehouse automatically creates the corresponding function.

Running `DROP FUNCTION public.upper_udf;` deletes the function and simultaneously removes the corresponding function from the cloud provider.

## UDAF

Supports developing functions based on the Hive 2.x UDAF specification. You can use [GenericUDAFResolver](https://github.com/apache/hive/blob/branch-2.3/ql/src/java/org/apache/hadoop/hive/ql/udf/generic/GenericUDAFResolver.java) and [GenericUDAFEvaluator](https://github.com/apache/hive/blob/branch-2.3/ql/src/java/org/apache/hadoop/hive/ql/udf/generic/GenericUDAFEvaluator.java) to develop a UDAF.

UDAF runtime environment:

Java: version 1.8 (JDK distribution provided by the cloud provider's Function Compute runtime environment).

Create a Maven project and add the dependency to `pom.xml`.

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

### UDAF Development

Write the UDAF code based on GenericUDAFResolver and GenericUDAFEvaluator.

```Java
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

### Upload the JAR File to a Volume

Compile and package as a JAR, then upload it to the user-specified object storage location or a Lakehouse Volume object.

```SQL
-- Upload the packaged UDF JAR
PUT '/Users/Downloads/sumint.jar' TO  VOLUME qn_hz_bucket_vol FILE 'sumint.jar';

-- View the uploaded files
SHOW VOLUME DIRECTORY qn_hz_bucket_vol;
```

```
relative_path url                           size last_modified_time  
------------- ----------------------------- ---- ------------------- 
upper.jar     oss://qn-hz-bucket/upper.jar  3161 2024-05-29 23:11:49 
sumint.jar    oss://qn-hz-bucket/sumint.jar 1022 2024-05-30 01:10:28 
```

### Create an External Function

1. Create a Connection object for the Function Compute service (see the UDF section above).
2. Create the External Function in the Lakehouse system.

Syntax for creating an External Function for a UDAF:

```SQL
CREATE EXTERNAL FUNCTION public.<funcName>
    AS '<className>'
    USING FILE 'oss://<bucket>/<pathToJar>'
    CONNECTION <connectionName>
    WITH PROPERTIES (
        'remote.udf.api' = 'java8.hive2.v0', 
        'remote.udf.category' = 'AGGREGATOR');
```

Parameter descriptions:

1. functionName: any valid identifier, e.g. `my_agg`
2. className: the fully qualified class name of the GenericUDAFResolver developed in step 1, e.g. `com.example.GenericUDAFSum`
3. bucket and pathToJar: the OSS bucket and object path uploaded in step 2
4. connectionName: the name of the connection created in step 3, e.g. `udf_deploy_0317`
5. Keep the last two PROPERTIES values as-is.

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

### Test Run

Test the UDF with sample data or table data. Note: you currently need to enable remote function access via the `cz.sql.remote.udf.enabled` parameter.

```SQL
-- Test run the UDF
set cz.sql.remote.udf.enabled = true;
select public.sumint(amount) from product_grossing;
```

## UDTF

### UDTF Development

Extend `org.apache.hadoop.hive.ql.udf.generic.GenericUDTF` to develop a UDTF. A UDTF must implement three methods: `initialize`, `process`, and `close`. The UDTF first calls `initialize`, which returns information about the output rows (count and types). After initialization, `process` is called to handle each set of input arguments; results are emitted via `forward()`. Finally, `close` is called for any required cleanup.

Write the UDTF code. Example:

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

### Upload the JAR File to a Volume

Compile and package as a JAR, then upload it to the user-specified object storage location or a Lakehouse Volume object.

```SQL
-- Upload the packaged UDF JAR
PUT '/Users/Downloads/MyExplode.jar' TO  VOLUME qn_hz_bucket_vol FILE 'MyExplode.jar';
```

### Create an External Function

1. Create a Connection object for the Function Compute service (see the UDF section above).
2. Create the External Function in the Lakehouse system.

Syntax for creating an External Function for a UDTF:

```SQL
CREATE EXTERNAL FUNCTION public.<funcName>
    AS '<className>'
    USING FILE 'oss://<bucket>/<pathToJar>'
    CONNECTION <connectionName>
    WITH PROPERTIES (
        'remote.udf.api' = 'java8.hive2.v0', 
        'remote.udf.category' = 'TABLE_VALUED');
```

Parameter descriptions:

1. functionName: any valid identifier, e.g. `my_udtf`
2. className: the fully qualified class name of the GenericUDTF developed in step 1, e.g. `com.example.MyGenericUDTF`
3. bucket and pathToJar: the OSS bucket and object path uploaded in step 2
4. connectionName: the name of the connection created in step 3, e.g. `my_function_conn`
5. Keep the last two PROPERTIES values as-is.
