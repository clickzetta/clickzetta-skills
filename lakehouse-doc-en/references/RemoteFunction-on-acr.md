# Processing Image Data Using Hugging Face Image Recognition Models

## 1. Applicable Scenarios:

This article creates a Remote Function based on Alibaba Cloud Container Registry images. This scenario is applicable when:

* If the Python dependency packages for the image recognition program exceed 500MB, you need to use the method described in this article, i.e., creating based on the Container Registry image service (if the function program package is less than 500MB, it can be directly uploaded to object storage for automated creation).
* Regardless of program file size, if you need to use GPU resources of the cloud Function Compute service, you need to create based on the Container Registry image service.

## 2. Demonstration Process:

### 2.1 Preparation

* Scenario: Use Hugging Face's image-to-text offline model to parse image content
* Model: Hugging Face image recognition model, see [link](https://huggingface.co/Salesforce/blip-image-captioning-large)
* Code: (see appendix)

### 2.2 Download Model and Dependencies:

(Recommended to run in an x86_64 Linux host environment)

#### 2.2.1 Download the Model

* Install the huggingface\_hub model download tool:

```Python
pip3 install huggingface_hub
```

* Download model files to the model directory; execute the following script using Python/ipython

  * repo\_id is the model name: Refer to the model website:

  ![](.topwrite/assets/remote_udf_image01.jpeg)

  * local\_dir: Local folder, the download destination for the model
  * local_dir_use_symlinks: Whether the local folder is a mount point

```Python
from huggingface_hub import snapshot_download
repo_id = 'nlpconnect/vit-gpt2-image-captioning'  
local_dir = './model'
local_dir_use_symlinks = False
snapshot_download(repo_id=repo_id, local_dir=local_dir, local_dir_use_symlinks=local_dir_use_symlinks)
```

#### 2.2.2 Download Dependencies:

Download dependencies to the `lib_` directory (requires a specific Python version; using Docker is recommended)

Create a `lib_ ` folder locally, mount it to Docker's `/root/lib_ `, and download the dependencies into `lib_`.

```Python
docker run -it -v `pwd`/lib_:/root/lib_ quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779 /bin/bash
```

Execute in the Docker environment:

```Python
cd /root
/opt/python/cp37-cp37m/bin/python3.7 -m venv venv
source venv/bin/activate
mkdir lib_
pip3 install \
    -i http://mirrors.cloud.aliyuncs.com/pypi/simple/ \
    --trusted-host mirrors.cloud.aliyuncs.com \
    transformers torch pillow \
    -t "./lib_"
```

^

### 2.3 Write Code:

Create a code file in the same directory level as ` model`, `lib_`, such as `hgf_image2text.py`. See the appendix for the code.

### 2.4 Test Code:

Test in the Docker environment `quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779`

```Python
docker run -it -v `pwd`:/app quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779 /bin/bash
```

Execute in the Docker environment:

```Python
cd /app
export PYTHONPATH=`pwd`:`pwd`/lib:`pwd`/lib_
python3 hgf_image2text.py https://huggingface.co/datasets/mishig/sample_images/resolve/main/savanna.jpg https://huggingface.co/datasets/mishig/sample_images/resolve/main/airport.jpg
```

After successful testing, package the image and upload it to the Alibaba Cloud ACR service.

### 2.5 Package and Upload Image:

#### 2.5.1 Prepare Image:

Create a Dockerfile in the same directory level as ` model`, `lib_`, and `hgf_image2text.py`, with the following content:

```Python
FROM quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779
RUN mkdir -p /app
WORKDIR /app
COPY . /app
```

Add the Singdata Lakehouse bootstrap program (contact Singdata support for access) and extract it to the current directory. At this point, the current directory should contain:

`model`, `lib_`, `hgf_image2text.py`, `Dockerfile` folders and files, as well as `bootstrap`, `lib`, `cz` extracted from the Singdata bootstrap program.

#### 2.5.2 Prepare Cloud Image Registry (requires logging into the Alibaba Cloud console):

1. Go to **Container Registry -> Instance List**, and **enter your personal instance**
   2. On the personal instance page, go to the left sidebar: **Repository Management** -> **Namespace** -> click **Create Namespace**: enter a namespace name, then **click Create**
   3. On the left sidebar: **Repository Management** -> **Image Repository** -> click **Create Image Repository**: **select a namespace**, **enter a repository name**, set the repository type to "**Private**" -> **Next**, choose **Local Repository** for the code source, then **click Create Image Repository**
   4. In the image repository list, enter the repository details page. The operation guide contains steps for uploading images; the **image version tag** is custom, for example for login:

```Shell
$ docker login --username=xxx@xxxx registry.cn-beijing.aliyuncs.com
```

#### 2.5.3 Upload Image (run locally):

Build the image:

```Shell
docker build -t registry.cn-beijing.aliyuncs.com/clickzetta/hgf_image2txt:hgf_i2t .
```

Push the image:

```Shell
docker push registry.cn-beijing.aliyuncs.com/clickzetta/hgf_image2txt:hgf_i2t
```

#### 2.5.4 Test the Image (run locally):

```Shell
docker run registry.cn-beijing.aliyuncs.com/clickzetta/hgf_image2txt:hgf_i2t /app/boostrap
```

^

### 2.6 Create Function (requires logging into the Alibaba Cloud console):

1. Go to **Function Compute FC 2.0 -> Services and Functions**, select the desired region at the top of the page; a popup will appear on the right to enter the service name, leave other settings as default; click **Show Advanced Options** at the bottom, select **AliyunFCDefaultRole** under **Service Role**, leave others as default (public network and VPC access policies can be chosen as desired)
2. In the **Service List**, enter the newly created service, click **Create Function**
3. On the **Create Function** page, choose **Create Using Container Image**; under **Basic Settings**: enter a **Function Name**, e.g., hgf\_image2txt, **Web Server Mode**: Yes, **Request Handler Type**: Process HTTP Requests
4. Under **Image Configuration**, select **Use Image in ACR**, choose the image in ACR, **Startup Command**: `/src/bootstrap`, **Listening Port**: 9000![](.topwrite/assets/remote_udf_image03.png)
5. Under **Advanced Configuration**, it is recommended to set vCPU and memory to 8 cores, 16GB
6. Leave other settings as default, click **Create**
7. In the **Function List**, enter the created function -> **Function Configuration**, **check the image acceleration preparation status**, wait until "**Available**"![](.topwrite/assets/remote_udf_image04.jpeg)
8. Enter **Trigger Management**, obtain the **public network access address HTTP link**![](.topwrite/assets/remote_udf_image05.jpeg)

***

#### 2.7 Create Remote Function in Singdata Lakehouse (operations on the Singdata Lakehouse side):

Create the function:

```SQL
create external function derek_fc_demo.hgf_image2text
as 'hgf_image2text.image_to_text'
with properties (
 -- Replace with the internal network access address HTTP link obtained when creating the function
 'remote.udf.url' = 'http://fc-imgtxt-hgf-imagetext-hdlrbwqdzg.cn-beijing.fcapp.run',
 'remote.udf.protocol' = 'http.arrow.v0'
);
```

Use the function (image URLs only support the https protocol):

```SQL
set cz.sql.remote.udf.enabled = true;
select derek_fc_demo.hgf_image2text("https://huggingface.co/datasets/mishig/sample_images/resolve/main/savanna.jpg")
```

## 3. Appendix

Code:

```Python
bash-3.2$ more hgf_image2text.py 

import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration,pipeline
from cz.udf import annotate

def _remove(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except:
        pass

def _wget(url, filepath):
    r = requests.get(url)
    with open(filepath, 'wb') as fd:
        fd.write(r.content)

_PIPELINE = None

processor = BlipProcessor.from_pretrained("./model")
model = BlipForConditionalGeneration.from_pretrained("./model")

@annotate("string->string")
class image_to_text(object):
    def __init__(self) -> None:
        global _PIPELINE
        if _PIPELINE is None:
            _PIPELINE = pipeline('image-to-text', model='./model')

    def evaluate(self,url):
        if url is None:
            return None
        try:
            img_url = url;
            raw_image = Image.open(requests.get(img_url, stream=True).raw).convert('RGB')
            text = "Clickzetta:A photography of"
            inputs = processor(raw_image, text, return_tensors="pt")
            out = model.generate(**inputs)
            print(processor.decode(out[0], skip_special_tokens=True))

            # unconditional image captioning
            inputs = processor(raw_image, return_tensors="pt")

            out = model.generate(**inputs)
            result = processor.decode(out[0], skip_special_tokens=True)

            if len(str(result)) >= 1:
                return str(result)
            else:
                return ""
        except Exception as exc:
            return "[error] " + exc.__str__()
        finally:
            pass 


if __name__ == "__main__":
    import sys
    to_text = image_to_text()
    for url in sys.argv[1:]:
        print(f"{to_text.evaluate(url)}")
```

^
