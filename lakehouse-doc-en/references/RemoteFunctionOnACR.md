# Using Hugging Face Image Recognition Model to Process Image Data

## 1. Applicable Scenarios:

This article creates a Remote Function based on Alibaba Cloud container images. This scenario is applicable for:

* If the image parsing program's Python + dependency package is larger than 500M, you need to use the method introduced in this article, which is to create based on the container image service (if the function's program file package is smaller than 500M, it can be directly uploaded to object storage for automated creation).
* Regardless of the program file size, if you need to use GPU resources of the cloud function computing service, you need to create based on the container image service.

## 2. Process Demonstration:

### 2.1 Preparation:

* Scenario: Use Hugging Face's image to text offline model to parse image content
* Model: Hugging Face's image recognition model, please refer to [link](https://huggingface.co/Salesforce/blip-image-captioning-large)
* Code: (see appendix)

### 2.2 Download Model and Dependency Libraries:

(Recommended to run in x86\_64 Linux host environment)

#### 2.2.1 Download Model

* Install huggingface\_hub model download tool:

```Python
pip3 install huggingface_hub
```

* Download the model file to the model directory, and execute the following script with Python/ipython

  * repo\_id is the model name: refer to the model website:

  ![](.topwrite/assets/remote_udf_image01.jpeg)

  * local\_dir: Local folder, the destination for model download
  * local\_dir\_use\_symlinks: Whether the local folder is a mount point

```Python
from huggingface_hub import snapshot_download
repo_id = 'nlpconnect/vit-gpt2-image-captioning'  
local_dir = './model'
local_dir_use_symlinks = False
snapshot_download(repo_id=repo_id, local_dir=local_dir, local_dir_use_symlinks=local_dir_use_symlinks)
```

#### 2.2.2 Download Dependencies:

Download the dependencies to the `lib_` directory (a specific version of Python is required, it is recommended to use Docker)

Create a `lib_` folder locally, mount it to Docker's `/root/lib_`, and download the dependencies into `lib_`

```Python
docker run -it -v `pwd`/lib_:/root/lib_ quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779 /bin/bash
```

Executing in Docker environment:

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

### 2.3 Writing Code:

Create a code file at the same directory level as `model` and `lib_`, such as `hgf_image2text.py`. Refer to the appendix for the code.

### 2.4 Testing Code:

Execute the test in the Docker `quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779`.

```Python
docker run -it -v `pwd`:/app quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779 /bin/bash
```

Executing in Docker environment:

```Python
cd /app
export PYTHONPATH=`pwd`:`pwd`/lib:`pwd`/lib_
python3 hgf_image2text.py https://huggingface.co/datasets/mishig/sample_images/resolve/main/savanna.jpg https://huggingface.co/datasets/mishig/sample_images/resolve/main/airport.jpg
```

After successful testing, package the image and upload it to Alibaba Cloud ACR service

### 2.5 Package and upload the image:

#### 2.5.1 Prepare the image:

Create a Dockerfile in the same directory as `model`, `lib_`, and `hgf_image2text.py`, with the following content:

```Python
FROM quay.io/pypa/manylinux2014_x86_64:2022-10-25-fbea779
RUN mkdir -p /app
WORKDIR /app
COPY . /app
```

Add the Singdata Lakehouse bootstrap program (you can contact Singdata support for assistance) and extract it to the current directory. At this point, the current directory should contain:

`model`, `lib_`, `hgf_image2text.py`, `Dockerfile` folders and files, as well as `bootstrap`, `lib`, `cz` extracted from the Singdata bootstrap program.

#### 2.5.2 Prepare the Cloud Image Repository (requires logging into the Alibaba Cloud console):

2. 1. Go to **Container Image Service -> Instance List**, **enter personal instance**
   2. In the personal instance interface, on the left side **Repository Management** -> **Namespace** -> Click **Create Namespace**: enter the namespace name, **click create**
   3. On the left side **Repository Management** -> **Image Repository** -> Click **Create Image Repository**: **select namespace**, **enter repository name, repository type** select "**Private**" -> **Next**, **Code Source** select **Local Repository**, **click create image repository**
   4. In the image repository list, enter the repository details page. The operation guide contains steps for uploading images, **image version number** is custom, for example: login:

```Shell
$ docker login --username=xxx@xxxx registry.cn-beijing.aliyuncs.com
```

#### 2.5.3 Upload Image (Local Execution):

Package the image:

```Shell
docker build -t registry.cn-beijing.aliyuncs.com/clickzetta/hgf_image2txt:hgf_i2t .
```

Uploading Image:

```Shell
docker push registry.cn-beijing.aliyuncs.com/clickzetta/hgf_image2txt:hgf_i2t
```

#### 2.5.4 Testing Image (Local Execution):

```Shell
docker run registry.cn-beijing.aliyuncs.com/clickzetta/hgf_image2txt:hgf_i2t /app/boostrap
```

### 2.6 Create Function (Login to Alibaba Cloud Console Required):

1. Go to **Function Compute FC 2.0 -> Services and Functions**, select the region you want to use at the top of the page, enter the service name in the pop-up page on the right, keep the rest as default; click **Show Advanced Options** at the bottom, **in the Service Role** select **AliyunFCDefaultRole**, keep the rest as default (Public Network and VPC access policies can be chosen as needed).
2. In the **Service List**, enter the service you just created, and click **Create Function**.
3. In the **Create Function** interface, select **Use** **Container Image**, in **Basic Settings**: enter **Function Name**, for example: hgf\_image2txt, **Web Server Mode**: Yes, **Request Handler Type**: Handle HTTP Requests.
4. In **Image Configuration**, select **Use Image from ACR**, choose the image from ACR, **Startup Command**: `/src/bootstrap`, **Listening Port**: 9000 ![](.topwrite/assets/20250225-195207.jpeg =774)
5. In **Advanced Configuration**, it is recommended to adjust the vCPU and memory to 8 cores, 16G.
6. Keep other configurations as default, and click **Create**.
7. In the **Function List**, enter the created function -> **Function Configuration**, **Check Image Acceleration Preparation Status**, wait until it shows "**Available**"![](.topwrite/assets/20250225-200410.jpeg =779)
8. Go to **Trigger Management**, obtain the **HTTP link for public network access**![](.topwrite/assets/hugging_face_p3.png)

***

#### 2.7 Create Remote Function in Singdata Lakehouse (Singdata Lakehouse Side Operation):

Create Function:

```SQL
create external function derek_fc_demo.hgf_image2text
as 'hgf_image2text.image_to_text'
with properties (
 -- Replace the internal network access address HTTP link obtained when creating the function here
 'remote.udf.url' = 'http://fc-imgtxt-hgf-imagetext-hdlrbwqdzg.cn-beijing.fcapp.run',
 'remote.udf.protocol' = 'http.arrow.v0'
);
```

Using the function (image URLs only recognize the https protocol):

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
