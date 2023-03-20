from __future__ import annotations

from docx import Document
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XML
import zipfile
from lxml import etree
import shutil
import tempfile
import openai
import os
import random
import docx2python

class XMLEdit:
    xml_tree: etree.Element
    xml_string: str
    template_path: str

    def __init__(self, template_path) -> None:
        self.xml_string = self.get_word_xml(template_path)
        self.xml_tree = self.get_xml_tree()
        self.template_path = template_path

    def fix_xml(self):
        # Need to think about how the xml is being stored and saved/updated. 
        pass

    def get_word_xml(self, path):
        zip = zipfile.ZipFile(path)
        xml_content = zip.read("word/document.xml")
        return xml_content

    def get_xml_tree(self):
        return etree.fromstring(self.xml_string)

    def _itertext(self, my_etree):
        """Iterator to go through xml tree's text nodes"""
        for node in my_etree.iter(tag=etree.Element):
            if self._check_element_is(node, "t"):
                yield (node, node.text)

    def _check_element_is(self, element, type_char):
        word_schema = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        return element.tag == "{%s}%s" % (word_schema, type_char)

    def find_and_replace_text(self):
        for node, txt in self._itertext(self.xml_tree):
            prompt = f"Replace the following text with something of similar length and subject: {txt}"
            node.text = self.generate_text(
                prompt=prompt, max_tokens=len(txt.split()) + len(prompt.split())
            )

    def generate_text(self, prompt: str, max_tokens: int) -> str:
        openai.api_key = os.environ.get("OPENAI_KEY", "")
        completion = openai.Completion.create(
            engine="text-davinci-003", prompt=prompt, max_tokens=max_tokens, echo=False
        )
        assert isinstance(completion, dict)
        text = random.choice(completion["choices"])["text"]
        return text

    def _write_and_close_docx(self, output_filename):
        """Create a temp directory, expand the original docx zip.
        Write the modified xml to word/document.xml
        Zip it up as the new docx
        """
        tmp_dir = tempfile.mkdtemp()

        zip = zipfile.ZipFile(self.template_path)
        zip.extractall(tmp_dir)

        with open(os.path.join(tmp_dir, "word/document.xml"), "wb") as f:
            xmlstr = etree.tostring(self.xml_tree, pretty_print=True)
            f.write(xmlstr)

        # Get a list of all the files in the original docx zipfile
        filenames = zip.namelist()
        # Now, create the new zip file and add all the filex into the archive
        zip_copy_filename = output_filename
        with zipfile.ZipFile(zip_copy_filename, "w") as docx:
            for filename in filenames:
                docx.write(os.path.join(tmp_dir, filename), filename)

        # Clean up the temp dir
        shutil.rmtree(tmp_dir)
